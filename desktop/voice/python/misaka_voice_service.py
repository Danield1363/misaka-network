#!/usr/bin/env python3
"""Misaka Native Voice Service — Vosk-based wake word + command detection.

Reads audio from the default microphone, transcribes with Vosk,
detects the "Misaka" wake phrase, extracts commands, and writes
JSON line-delimited events to stdout.

Usage:
    python misaka_voice_service.py [--model PATH]

Events (one JSON object per line on stdout):
    {"type":"status","state":"listening_for_wake","message":"..."}
    {"type":"transcript","text":"..."}
    {"type":"command","command":"...","source":"native_voice"}
    {"type":"error","error":"...","message":"..."}
"""

import argparse
import json
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WAKE_PHRASES = ["misaka", "ei misaka", "ok misaka", "acorda misaka"]

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "models", "pt"
)

COMMAND_TIMEOUT_MS = 8000

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def emit(obj: dict) -> None:
    """Write a JSON line to stdout and flush."""
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def normalize_text(text: str) -> str:
    """Lowercase, strip accents, remove punctuation, collapse spaces."""
    text = unicodedata.normalize("NFD", text.lower().strip())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_command(text: str) -> str | None:
    """If text contains a wake phrase, return the command after it.

    Returns:
        The command string (may be empty if user only said the wake word).
        None if no wake phrase found.
    """
    normalized = normalize_text(text)
    phrases = sorted(
        [normalize_text(p) for p in WAKE_PHRASES], key=len, reverse=True
    )

    matched = None
    for phrase in phrases:
        if normalized == phrase or normalized.startswith(phrase + " "):
            matched = phrase
            break

    if matched is None:
        return None

    raw_pattern = re.compile(
        r"^\s*(?:(?:ei|ok|acorda)\s+)?misaka\b[\s,.;:!?-]*", re.IGNORECASE
    )
    command = raw_pattern.sub("", text).strip()
    return command


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def run(model_path: str) -> None:
    """Initialize Vosk, open microphone, and process audio."""
    try:
        from vosk import Model, KaldiRecognizer, SetLogLevel
    except ImportError:
        emit(
            {
                "type": "error",
                "error": "vosk_not_installed",
                "message": (
                    "Vosk não está instalado. "
                    "Execute: pip install -r requirements.txt"
                ),
            }
        )
        return

    SetLogLevel(-1)

    if not os.path.isdir(model_path):
        emit(
            {
                "type": "error",
                "error": "model_not_found",
                "message": (
                    "Modelo de voz nativo não encontrado. "
                    "Baixe um modelo Vosk pt-BR e coloque em "
                    f"{os.path.abspath(model_path)}"
                ),
            }
        )
        return

    try:
        model = Model(model_path)
    except Exception as exc:
        emit(
            {
                "type": "error",
                "error": "model_load_failed",
                "message": f"Falha ao carregar modelo Vosk: {exc}",
            }
        )
        return

    try:
        import sounddevice as sd

        samplerate = int(sd.query_devices(kind="input")["default_samplerate"])
    except Exception as exc:
        emit(
            {
                "type": "error",
                "error": "microphone_error",
                "message": f"Microfone não encontrado ou bloqueado: {exc}",
            }
        )
        return

    recognizer = KaldiRecognizer(model, samplerate)
    recognizer.SetWords(True)

    waiting_for_command = False

    emit({"type": "status", "state": "listening_for_wake", "message": "Ouvindo por Misaka"})

    try:
        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=8000,
            dtype="int16",
            channels=1,
        ) as stream:
            while True:
                data, overflowed = stream.read(8000)
                if overflowed:
                    pass

                if recognizer.AcceptWaveform(bytes(data)):
                    result = json.loads(recognizer.Result())
                    text = (result.get("text") or "").strip()
                    if not text:
                        continue

                    emit({"type": "transcript", "text": text})

                    command = extract_command(text)
                    if command is None:
                        continue

                    if command:
                        emit(
                            {
                                "type": "command",
                                "command": command,
                                "source": "native_voice",
                            }
                        )
                        waiting_for_command = False
                    else:
                        waiting_for_command = True
                        emit(
                            {
                                "type": "status",
                                "state": "wake_detected",
                                "message": "Wake detectado. Aguardando comando...",
                            }
                        )
                else:
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = (partial.get("partial") or "").strip()
                    if partial_text:
                        emit({"type": "transcript", "text": partial_text})

    except KeyboardInterrupt:
        pass
    except Exception as exc:
        emit(
            {
                "type": "error",
                "error": "runtime_error",
                "message": f"Erro no serviço de voz: {exc}",
            }
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Misaka Native Voice Service")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_PATH,
        help="Path to Vosk model directory (default: desktop/voice/models/pt)",
    )
    args = parser.parse_args()
    run(args.model)


if __name__ == "__main__":
    main()
