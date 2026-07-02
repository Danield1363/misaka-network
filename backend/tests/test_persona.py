import pytest
from app.persona.formatter import ResponseFormatter
from app.persona.engine import PersonaEngine


def test_formatter_appends_suffix():
    formatter = ResponseFormatter(suffix_enabled=True, suffix_text="diz Misaka Misaka.")
    result = formatter.format("Olá")
    assert "diz Misaka Misaka." in result


def test_formatter_no_suffix():
    formatter = ResponseFormatter(suffix_enabled=False)
    result = formatter.format("Olá")
    assert "diz Misaka" not in result


def test_formatter_no_duplicate_suffix():
    formatter = ResponseFormatter(suffix_enabled=True, suffix_text="diz Misaka Misaka.")
    result = formatter.format("Olá diz Misaka Misaka.")
    assert result.count("diz Misaka Misaka.") == 1


def test_formatter_ensures_punctuation():
    formatter = ResponseFormatter(suffix_enabled=False)
    result = formatter.format("Olá")
    assert result.endswith(".")


def test_formatter_cleans_spaces():
    formatter = ResponseFormatter(suffix_enabled=False)
    result = formatter.format("Olá   mundo")
    assert "  " not in result


def test_persona_engine_system_prompt():
    engine = PersonaEngine()
    prompt = engine.get_system_prompt()
    assert "Misaka" in prompt


def test_persona_engine_format_response():
    engine = PersonaEngine()
    result = engine.format_response("Teste")
    assert "diz Misaka Misaka." in result


def test_persona_engine_profile():
    engine = PersonaEngine()
    profile = engine.get_profile()
    assert profile["name"] == "Misaka"
    assert profile["suffix_enabled"] is True