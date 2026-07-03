#!/usr/bin/env python3
"""Misaka Voice Daemon — Always-on local voice command system.

Runs a WebSocket server on 127.0.0.1:8765, listens to the microphone,
transcribes with Vosk, detects commands, and sends JSON events.

Usage:
    python misaka_voice_daemon.py [--model PATH] [--port 8765]

Events (JSON lines over WebSocket):
    {"type":"status","state":"listening","message":"..."}
    {"type":"transcript","text":"..."}
    {"type":"command","command":"...","source":"native_voice","mode":"..."}
    {"type":"error","error":"...","message":"..."}
"""

import argparse
import asyncio
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

SAFE_PREFIXES = [
    "abrir", "abra", "abre", "iniciar", "inicia",
    "executar", "execute", "rodar", "roda", "rode",
    "pesquisar", "pesquise", "procurar", "procure",
    "buscar", "busque",
    "ative", "ativar", "desative", "desativar",
    "limpe", "limpar", "mostrar", "mostre",
    "atualizar", "atualize",
]

DANGEROUS_PATTERNS = [
    r"desligar\s+(o\s+)?computador",
    r"desligar\s+pc",
    r"reiniciar\s+(o\s+)?computador",
    r"reiniciar\s+pc",
    r"apagar\s+arquivo",
    r"deletar\s+arquivo",
    r"formatar",
    r"executar\s+comando",
    r"rodar\s+script",
    r"enviar\s+mensagem",
    r"comprar",
    r"pagar",
    r"remover\s+(o\s+)?sistema",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def emit(obj):
    """Serialize dict to JSON string."""
    return json.dumps(obj, ensure_ascii=False)


def normalize_text(text):
    text = unicodedata.normalize("NFD", text.lower().strip())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_command_from_wake_phrase(text):
    raw = str(text or "").strip()
    if not raw:
        return None
    normalized = normalize_text(raw)
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
    return raw_pattern.sub("", raw).strip()


def is_direct_command(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    for verb in SAFE_PREFIXES:
        if normalized.startswith(verb + " ") or normalized == verb:
            return True
    return False


def classify_command(text):
    normalized = normalize_text(text)
    if not normalized:
        return {"matched": False}
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, normalized):
            return {
                "matched": True,
                "command": normalized,
                "mode": "direct_command",
                "risk": "dangerous",
                "requires_confirmation": True,
            }
    for verb in SAFE_PREFIXES:
        if normalized.startswith(verb + " ") or normalized == verb:
            return {
                "matched": True,
                "command": normalized,
                "mode": "direct_command",
                "risk": "safe",
                "requires_confirmation": False,
            }
    return {"matched": False}


# ---------------------------------------------------------------------------
# Voice processing
# ---------------------------------------------------------------------------


def process_transcript(text, voice_command_mode="hybrid"):
    """Process a transcript and return (command_text, classification) or (None, None)."""
    clean = str(text or "").strip()
    if not clean:
        return None, None

    # Try wake phrase first
    wake_cmd = extract_command_from_wake_phrase(clean)
    if wake_cmd is not None:
        if wake_cmd:
            return wake_cmd, {"matched": True, "mode": "wake_word", "risk": "safe"}
        return "", {"matched": False}  # just "Misaka" with no command

    # Direct command mode
    if voice_command_mode in ("direct_command", "hybrid"):
        classification = classify_command(clean)
        if classification["matched"]:
            return clean, classification

    return None, None


# ---------------------------------------------------------------------------
# WebSocket server
# ---------------------------------------------------------------------------


async def handle_client(websocket, model_path, voice_command_mode):
    """Handle a single WebSocket client connection."""
    try:
        import sounddevice as sd
        from vosk import Model, KaldiRecognizer, SetLogLevel

        SetLogLevel(-1)
    except ImportError as exc:
        await websocket.send(emit({
            "type": "error",
            "error": "dependency_missing",
            "message": f"Dependencia faltando: {exc}. Execute: pip install -r requirements.txt",
        }))
        return

    if not os.path.isdir(model_path):
        await websocket.send(emit({
            "type": "error",
            "error": "model_not_found",
            "message": (
                "Modelo de voz nativo nao encontrado. "
                "Baixe um modelo Vosk pt-BR e coloque em "
                f"{os.path.abspath(model_path)}"
            ),
        }))
        return

    try:
        model = Model(model_path)
    except Exception as exc:
        await websocket.send(emit({
            "type": "error",
            "error": "model_load_failed",
            "message": f"Falha ao carregar modelo Vosk: {exc}",
        }))
        return

    try:
        device_info = sd.query_devices(kind="input")
        samplerate = int(device_info["default_samplerate"])
    except Exception as exc:
        await websocket.send(emit({
            "type": "error",
            "error": "microphone_error",
            "message": f"Microfone nao encontrado ou bloqueado: {exc}",
        }))
        return

    recognizer = KaldiRecognizer(model, samplerate)
    recognizer.SetWords(True)

    await websocket.send(emit({
        "type": "status",
        "state": "listening",
        "message": "Misaka Voice Daemon ouvindo comandos.",
    }))

    try:
        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=8000,
            dtype="int16",
            channels=1,
        ) as stream:
            while True:
                data, _ = stream.read(8000)

                if recognizer.AcceptWaveform(bytes(data)):
                    result = json.loads(recognizer.Result())
                    text = (result.get("text") or "").strip()
                    if not text:
                        continue

                    await websocket.send(emit({
                        "type": "transcript",
                        "text": text,
                    }))

                    cmd_text, classification = process_transcript(
                        text, voice_command_mode
                    )
                    if cmd_text is not None and classification and classification.get("matched"):
                        await websocket.send(emit({
                            "type": "command",
                            "command": cmd_text,
                            "source": "native_voice",
                            "mode": classification.get("mode", "direct_command"),
                        }))
                else:
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = (partial.get("partial") or "").strip()
                    if partial_text:
                        await websocket.send(emit({
                            "type": "transcript",
                            "text": partial_text,
                        }))

    except Exception as exc:
        await websocket.send(emit({
            "type": "error",
            "error": "runtime_error",
            "message": f"Erro no servico de voz: {exc}",
        }))


async def run_server(host, port, model_path, voice_command_mode):
    """Start the WebSocket server."""
    try:
        import websockets
    except ImportError:
        print(json.dumps({
            "type": "error",
            "error": "websockets_not_installed",
            "message": "websockets nao instalado. Execute: pip install websockets",
        }))
        sys.exit(1)

    async def handler(websocket):
        await handle_client(websocket, model_path, voice_command_mode)

    async with websockets.serve(handler, host, port):
        print(json.dumps({
            "type": "status",
            "state": "ready",
            "message": f"Misaka Voice Daemon rodando em ws://{host}:{port}",
        }), flush=True)
        await asyncio.Future()  # run forever


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Misaka Voice Daemon")
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--mode", default="hybrid",
                        choices=["wake_word", "direct_command", "hybrid"])
    args = parser.parse_args()

    asyncio.run(run_server(args.host, args.port, args.model, args.mode))


if __name__ == "__main__":
    main()
