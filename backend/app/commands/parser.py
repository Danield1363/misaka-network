import re
from app.commands.intents import INTENT_MAP, Intent


def normalize_message(message: str) -> str:
    text = message.lower().strip()
    text = re.sub(r'[^\w\sàáâãéêíóôõúüç]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def detect_intent(message: str) -> Intent | None:
    normalized = normalize_message(message)

    best_match = None
    best_score = 0

    for intent_name, config in INTENT_MAP.items():
        for keyword in config["keywords"]:
            kw_lower = keyword.lower()
            if kw_lower in normalized:
                score = len(kw_lower) / len(normalized) if len(normalized) > 0 else 0
                if normalized.startswith(kw_lower):
                    score += 0.3
                if score > best_score:
                    best_score = score
                    best_match = Intent(
                        name=intent_name,
                        confidence=min(score + 0.5, 1.0),
                        tool_name=config.get("tool_name"),
                        requires_confirmation=config.get("requires_confirmation", False),
                        response_message=config.get("response_message", ""),
                        parameters=config.get("parameters", {})
                    )

    return best_match


def extract_task_description(message: str) -> str:
    patterns = [
        r"cri[eé]\s+(?:uma?\s+)?tarefa\s+(?:para?\s+)?(.+)",
        r"nova\s+tarefa\s*[:]\s*(.+)",
        r"adicione\s+(?:uma?\s+)?tarefa\s*[:]\s*(.+)",
        r"tarefa\s*[:]\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            return match.group(1).strip()
    return message


def extract_reminder_text(message: str) -> str:
    patterns = [
        r"me\s+lembre\s+(?:de\s+)?(.+)",
        r"crie\s+(?:um\s+)?lembrete\s+(?:para?\s+)?(.+)",
        r"lembrete\s*[:]\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            return match.group(1).strip()
    return message


def extract_memory_content(message: str) -> str:
    patterns = [
        r"lembre\s+que\s+(.+)",
        r"salve\s+(?:isso\s+)?na\s+mem[oó]ria\s*[:]\s*(.+)",
        r"guarde\s+(?:isso\s+)?[:]\s*(.+)",
        r"anote\s+que\s+(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            return match.group(1).strip()
    return message


def extract_app_name(message: str) -> str:
    app_map = {
        "discord": "discord",
        "vscode": "vscode",
        "vs code": "vscode",
        "explorer": "explorer",
        "youtube": "youtube",
        "chrome": "browser",
        "firefox": "browser",
        "edge": "browser",
        "navegador": "browser",
        "notepad": "notepad",
        "terminal": "terminal",
        "music": "music",
    }
    lower = message.lower()
    for key, value in app_map.items():
        if key in lower:
            return value
    return "browser"


def extract_search_query(message: str) -> str:
    patterns = [
        r"pesquise\s+por\s+(.+)",
        r"pesquisar\s+(.+)",
        r"procure\s+por\s+(.+)",
        r"busque\s+por\s+(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            return match.group(1).strip()
    return ""
