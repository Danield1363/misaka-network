import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.brain.planner import Planner


def test_planner_detects_tasks():
    planner = Planner()
    # "cria tarefa" doesn't match command keywords exactly (parser uses "crie uma tarefa")
    # so planner's task keywords match
    assert planner.detect_intent("cria tarefa estudar Python") == "tasks"
    assert planner.detect_intent("minhas tarefas") == "tasks"
    # "nova tarefa" is an exact keyword match in INTENT_MAP, so command router catches it
    assert planner.detect_intent("nova tarefa") == "command"


def test_planner_detects_coding():
    planner = Planner()
    assert planner.detect_intent("python é legal") == "coding"
    assert planner.detect_intent("fastapi tutorial") == "coding"
    assert planner.detect_intent("tem um bug") == "coding"


def test_planner_detects_conversation():
    planner = Scanner = Planner()
    assert planner.detect_intent("olá") == "conversation"