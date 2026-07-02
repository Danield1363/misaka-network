import pytest
from app.commands.parser import detect_intent
from app.commands.intents import Intent, INTENT_MAP


def test_detect_clear_alerts():
    result = detect_intent("limpe os alertas atuais")
    assert result is not None
    assert result.name == "clear_alerts"
    assert result.confidence > 0.5


def test_detect_ack_all():
    result = detect_intent("marque os alertas como vistos")
    assert result is not None
    assert result.name == "clear_alerts"
    assert result.confidence > 0.5


def test_detect_hud_enable():
    result = detect_intent("ative o modo hud")
    assert result is not None
    assert result.name == "hud_on"
    assert result.confidence > 0.5


def test_detect_hud_disable():
    result = detect_intent("desative o modo hud")
    assert result is not None
    assert result.name == "hud_off"


def test_detect_open_settings():
    result = detect_intent("abra configurações")
    assert result is not None
    assert result.name == "open_settings"


def test_detect_clear_chat():
    result = detect_intent("limpe o chat")
    assert result is not None
    assert result.name == "clear_chat"


def test_detect_voice_enable():
    result = detect_intent("ligue a voz")
    assert result is not None
    assert result.name == "voice_on"


def test_detect_voice_disable():
    result = detect_intent("desligue a voz")
    assert result is not None
    assert result.name == "voice_off"


def test_detect_open_browser():
    result = detect_intent("abra o navegador")
    assert result is not None
    assert result.name == "open_browser"


def test_detect_open_discord():
    result = detect_intent("abra o discord")
    assert result is not None
    assert result.name == "open_app"


def test_detect_search():
    result = detect_intent("pesquise por receitas de bolo")
    assert result is not None
    assert result.name == "search_web"


def test_detect_pc_status():
    result = detect_intent("qual o status do meu pc")
    assert result is not None
    assert result.name == "pc_status"


def test_detect_create_task():
    result = detect_intent("crie uma tarefa")
    assert result is not None
    assert result.name == "create_task"


def test_detect_list_tasks():
    result = detect_intent("liste minhas tarefas")
    assert result is not None
    assert result.name == "list_tasks"


def test_detect_reminder():
    result = detect_intent("me lembre de comprar leite")
    assert result is not None
    assert result.name == "create_reminder"


def test_detect_memory_save():
    result = detect_intent("lembre que eu gosto de pizza")
    assert result is not None
    assert result.name == "remember"


def test_detect_memory_search():
    result = detect_intent("o que você lembra sobre mim")
    assert result is not None
    assert result.name == "recall"


def test_detect_android_vibrate():
    result = detect_intent("faça meu celular vibrar")
    assert result is not None
    assert result.name == "android_vibrate"


def test_detect_show_alerts():
    result = detect_intent("mostrar alertas")
    assert result is not None
    assert result.name == "show_alerts"


def test_detect_conversation():
    result = detect_intent("como vai você?")
    assert result is None


def test_normalize_removes_punctuation():
    result = detect_intent("limpe os alertas atuais!")
    assert result is not None
    assert result.name == "clear_alerts"


@pytest.mark.asyncio
async def test_router_clear_alerts():
    from app.commands.router import CommandRouter
    router = CommandRouter()
    result = await router.route("limpe os alertas atuais")
    assert result is not None
    assert result["type"] == "command_executed"
    assert result["intent"] == "clear_alerts"


@pytest.mark.asyncio
async def test_router_hud_enable():
    from app.commands.router import CommandRouter
    router = CommandRouter()
    result = await router.route("ative o modo hud")
    assert result is not None
    assert result["type"] == "command_executed"
    assert result["intent"] == "hud_on"


@pytest.mark.asyncio
async def test_router_conversation_returns_none():
    from app.commands.router import CommandRouter
    router = CommandRouter()
    result = await router.route("como vai você?")
    assert result is None


def test_intent_map_has_required_intents():
    required = [
        "clear_alerts", "show_alerts", "hud_on", "hud_off",
        "open_settings", "clear_chat", "voice_on", "voice_off",
        "open_browser", "open_app", "search_web", "pc_status",
        "create_task", "list_tasks", "remember", "recall",
        "create_reminder", "android_vibrate",
    ]
    for intent in required:
        assert intent in INTENT_MAP, f"Missing intent: {intent}"


def test_intent_has_tool_name():
    for name, config in INTENT_MAP.items():
        assert "tool_name" in config, f"Intent {name} missing tool_name"
        assert "keywords" in config, f"Intent {name} missing keywords"
        assert len(config["keywords"]) > 0, f"Intent {name} has no keywords"
