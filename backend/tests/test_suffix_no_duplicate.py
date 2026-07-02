import pytest
from app.persona.formatter import ResponseFormatter


def test_suffix_added_once():
    formatter = ResponseFormatter(suffix_enabled=True, suffix_text="diz Misaka Misaka.")
    result = formatter.format("Olá, como vai?")
    assert result.count("diz Misaka Misaka.") == 1


def test_suffix_not_duplicated_when_already_present():
    formatter = ResponseFormatter(suffix_enabled=True, suffix_text="diz Misaka Misaka.")
    result = formatter.format("Olá, como vai? diz Misaka Misaka.")
    assert result.count("diz Misaka Misaka.") == 1


def test_suffix_not_added_when_disabled():
    formatter = ResponseFormatter(suffix_enabled=False, suffix_text="diz Misaka Misaka.")
    result = formatter.format("Olá, como vai?")
    assert "diz Misaka Misaka." not in result


def test_suffix_case_insensitive():
    formatter = ResponseFormatter(suffix_enabled=True, suffix_text="diz Misaka Misaka.")
    result = formatter.format("Olá. Diz Misaka Misaka.")
    assert result.count("Misaka") == 2


def test_suffix_punctuation_handled():
    formatter = ResponseFormatter(suffix_enabled=True, suffix_text="diz Misaka Misaka.")
    result = formatter.format("Olá, como vai!")
    assert result.endswith("diz Misaka Misaka.")
    assert "!" not in result.split("diz Misaka Misaka.")[-1]
