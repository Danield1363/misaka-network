#!/usr/bin/env python3
"""Check Misaka Voice Daemon setup requirements."""

import json
import os
import subprocess
import sys

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "pt")
REQUIREMENTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")


def check_python():
    return {
        "found": True,
        "command": sys.executable or "python",
        "version": sys.version.split()[0],
    }


def check_requirements():
    req_file = os.path.exists(REQUIREMENTS_PATH)
    installed = True
    missing = []
    for pkg in ["vosk", "sounddevice", "websockets"]:
        try:
            __import__(pkg)
        except ImportError:
            installed = False
            missing.append(pkg)
    return {
        "file_exists": req_file,
        "installed": installed,
        "missing": missing,
    }


def check_model():
    return {
        "exists": os.path.isdir(MODEL_PATH),
        "path": os.path.abspath(MODEL_PATH),
    }


def check_daemon():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect(("127.0.0.1", 8765))
        running = True
    except (ConnectionRefusedError, OSError):
        running = False
    finally:
        sock.close()
    return {
        "running": running,
        "websocket": "ws://127.0.0.1:8765",
    }


def diagnose():
    python = check_python()
    requirements = check_requirements()
    model = check_model()
    daemon = check_daemon()

    next_step = ""
    if not python["found"]:
        next_step = "Instale Python e marque a opcao Add Python to PATH."
    elif not requirements["installed"]:
        pkgs = ", ".join(requirements["missing"])
        next_step = f"Rode: python -m pip install -r desktop/voice/python/requirements.txt (faltando: {pkgs})"
    elif not model["exists"]:
        next_step = "Baixe um modelo Vosk pt-BR e coloque em desktop/voice/models/pt."
    elif not daemon["running"]:
        next_step = "Daemon nao esta rodando. Clique em Iniciar Daemon."
    else:
        next_step = "Tudo pronto! O daemon esta rodando."

    return {
        "success": True,
        "python": python,
        "requirements": requirements,
        "model": model,
        "daemon": daemon,
        "next_step": next_step,
    }


if __name__ == "__main__":
    result = diagnose()
    print(json.dumps(result, indent=2, ensure_ascii=False))
