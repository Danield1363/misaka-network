import pytest
from app.commands.desktop_resolver import detect_desktop_command


def test_notepad_ptbr():
    cmd = detect_desktop_command("abrir notepad no meu computador")
    assert cmd.matched is True
    assert cmd.app == "notepad"
    assert cmd.command == "open_app"


def test_notepad_simple():
    cmd = detect_desktop_command("abra o notepad")
    assert cmd.matched is True
    assert cmd.app == "notepad"


def test_notepad_bloco():
    cmd = detect_desktop_command("abrir bloco de notas")
    assert cmd.matched is True
    assert cmd.app == "notepad"


def test_notepad_bloco_notas():
    cmd = detect_desktop_command("abra o bloco de notas")
    assert cmd.matched is True
    assert cmd.app == "notepad"


def test_discord():
    cmd = detect_desktop_command("abra o discord")
    assert cmd.matched is True
    assert cmd.app == "discord"


def test_discord_pc():
    cmd = detect_desktop_command("abra o discord no pc")
    assert cmd.matched is True
    assert cmd.app == "discord"


def test_vscode():
    cmd = detect_desktop_command("abra o vs code")
    assert cmd.matched is True
    assert cmd.app == "vscode"


def test_vscode_computador():
    cmd = detect_desktop_command("abra o vs code no meu computador")
    assert cmd.matched is True
    assert cmd.app == "vscode"


def test_explorer():
    cmd = detect_desktop_command("abra o explorer")
    assert cmd.matched is True
    assert cmd.app == "explorer"


def test_explorer_arquivos():
    cmd = detect_desktop_command("abrir explorador de arquivos")
    assert cmd.matched is True
    assert cmd.app == "explorer"


def test_calculator():
    cmd = detect_desktop_command("iniciar calculadora")
    assert cmd.matched is True
    assert cmd.app == "calculator"


def test_chrome():
    cmd = detect_desktop_command("abra o chrome")
    assert cmd.matched is True
    assert cmd.app == "chrome"


def test_edge():
    cmd = detect_desktop_command("abra o edge")
    assert cmd.matched is True
    assert cmd.app == "edge"


def test_cmd():
    cmd = detect_desktop_command("abra cmd")
    assert cmd.matched is True
    assert cmd.app == "cmd"


def test_powershell():
    cmd = detect_desktop_command("abra powershell")
    assert cmd.matched is True
    assert cmd.app == "powershell"


def test_abrir_discord_without_article():
    cmd = detect_desktop_command("abrir discord")
    assert cmd.matched is True
    assert cmd.app == "discord"


def test_conversation_not_matched():
    cmd = detect_desktop_command("como vai você?")
    assert cmd.matched is False


def test_empty_not_matched():
    cmd = detect_desktop_command("")
    assert cmd.matched is False


def test_no_verb_low_confidence():
    cmd = detect_desktop_command("notepad")
    assert cmd.matched is True
    assert cmd.confidence < 0.95


def test_confidence_high_with_verb():
    cmd = detect_desktop_command("abra o discord")
    assert cmd.confidence >= 0.95
