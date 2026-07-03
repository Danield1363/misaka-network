#!/usr/bin/env python3
"""Tests for voice parser functions."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from misaka_voice_daemon import (
    normalize_text,
    extract_command_from_wake_phrase,
    is_direct_command,
    classify_command,
    process_transcript,
)

assert normalize_text("ABRIR YouTube!!!") == "abrir youtube"
assert normalize_text("Ei Misaka, abrir notepad") == "ei misaka abrir notepad"

assert extract_command_from_wake_phrase("Misaka, abrir youtube") == "abrir youtube"
assert extract_command_from_wake_phrase("Ei Misaka abre o Discord") == "abre o Discord"
assert extract_command_from_wake_phrase("Ok Misaka, limpe os alertas") == "limpe os alertas"
assert extract_command_from_wake_phrase("Misaka") == ""
assert extract_command_from_wake_phrase("aloh teste") is None

assert is_direct_command("abrir youtube") is True
assert is_direct_command("abra o discord") is True
assert is_direct_command("abrir notepad no meu computador") is True
assert is_direct_command("pesquise wake on lan no google") is True
assert is_direct_command("procure alanzoka no youtube") is True
assert is_direct_command("limpe os alertas") is True
assert is_direct_command("ative o hud") is True
assert is_direct_command("qual e a capital do brasil") is False
assert is_direct_command("como vai voce") is False
assert is_direct_command("") is False

safe = classify_command("abrir youtube")
assert safe["matched"] is True
assert safe["risk"] == "safe"
assert safe["requires_confirmation"] is False

safe2 = classify_command("pesquise wake on lan no google")
assert safe2["matched"] is True
assert safe2["risk"] == "safe"

dangerous = classify_command("desligar computador")
assert dangerous["matched"] is True
assert dangerous["risk"] == "dangerous"
assert dangerous["requires_confirmation"] is True

dangerous2 = classify_command("reiniciar pc")
assert dangerous2["matched"] is True
assert dangerous2["risk"] == "dangerous"

dangerous3 = classify_command("formatar")
assert dangerous3["matched"] is True
assert dangerous3["risk"] == "dangerous"

nomatch = classify_command("qual e a capital do brasil")
assert nomatch["matched"] is False

cmd1, cls1 = process_transcript("Misaka, abrir youtube")
assert cmd1 == "abrir youtube"
assert cls1["matched"] is True
assert cls1["mode"] == "wake_word"

cmd2, cls2 = process_transcript("abrir youtube", "hybrid")
assert cmd2 == "abrir youtube"
assert cls2["matched"] is True
assert cls2["mode"] == "direct_command"

cmd3, cls3 = process_transcript("abrir youtube", "wake_word")
assert cmd3 is None

cmd4, cls4 = process_transcript("")
assert cmd4 is None

print("voice parser tests passed")
