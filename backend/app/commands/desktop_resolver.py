import re
import unicodedata
from dataclasses import dataclass


APP_ALIASES = {
    "notepad": "notepad",
    "bloco de notas": "notepad",
    "bloco notas": "notepad",
    "bloco": "notepad",
    "calculadora": "calculator",
    "calculator": "calculator",
    "calc": "calculator",
    "explorer": "explorer",
    "explorador de arquivos": "explorer",
    "explorador": "explorer",
    "arquivos": "explorer",
    "files": "explorer",
    "vscode": "vscode",
    "visual studio code": "vscode",
    "vs code": "vscode",
    "code": "vscode",
    "discord": "discord",
    "navegador": "browser",
    "browser": "browser",
    "google chrome": "chrome",
    "chrome": "chrome",
    "microsoft edge": "edge",
    "edge": "edge",
    "firefox": "firefox",
    "prompt de comando": "cmd",
    "prompt": "cmd",
    "cmd": "cmd",
    "power shell": "powershell",
    "powershell": "powershell",
}

WEB_TARGETS = {
    "youtube",
    "yt",
    "google",
    "github",
    "reddit",
    "modrinth",
    "curseforge",
    "wikipedia",
    "twitch",
    "steam",
    "nexusmods",
    "site",
    "canal",
    "video",
    "vídeo",
}

INTERNAL_COMMAND_TARGETS = {
    "configuracoes",
    "settings",
    "alertas",
    "chat",
    "hud",
    "voz",
    "voice",
}

VERB_PATTERNS = [
    r"\babrir\b",
    r"\babra\b",
    r"\babre\b",
    r"\biniciar\b",
    r"\binicia\b",
    r"\bexecutar\b",
    r"\bexecute\b",
    r"\brodar\b",
    r"\broda\b",
    r"\brode\b",
    r"\bchama\b",
    r"\bchamar\b",
]

TARGET_PATTERNS = [
    r"no\s+meu\s+computador",
    r"no\s+computador",
    r"no\s+pc",
    r"no\s+desktop",
    r"na\s+minha\s+maquina",
    r"localmente",
]

APP_LABELS = {
    "notepad": "Bloco de Notas",
    "calculator": "Calculadora",
    "explorer": "Explorador de Arquivos",
    "vscode": "VS Code",
    "discord": "Discord",
    "browser": "Navegador",
    "chrome": "Chrome",
    "edge": "Edge",
    "firefox": "Firefox",
    "cmd": "Prompt de Comando",
    "powershell": "PowerShell",
}


@dataclass
class DesktopCommand:
    matched: bool = False
    intent: str = ""
    command: str = ""
    app: str = ""
    target_device: str = "desktop"
    confidence: float = 0.0
    response_message: str = ""


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().strip())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def resolve_app_name(text: str) -> str | None:
    normalized = normalize_text(text)
    best_match = None
    best_len = 0
    for alias, app_name in sorted(APP_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            if len(alias) > best_len:
                best_len = len(alias)
                best_match = app_name
    return best_match


def extract_unknown_app_name(text: str) -> str | None:
    normalized = normalize_text(text)
    match = re.search(
        r"\b(?:abrir|abra|abre|iniciar|inicia|executar|execute|rodar|roda|rode|chamar|chama)\s+(?:o\s+|a\s+|os\s+|as\s+)?(.+)$",
        normalized,
    )
    if not match:
        return None

    candidate = match.group(1).strip()
    candidate = re.sub(
        r"\s+(?:no\s+meu\s+computador|no\s+computador|no\s+pc|no\s+desktop|na\s+minha\s+maquina|localmente)$",
        "",
        candidate,
    ).strip()
    candidate = re.sub(r"^(?:app|aplicativo|programa)\s+", "", candidate).strip()

    if not candidate or len(candidate) > 48:
        return None
    first_word = candidate.split()[0]
    if (
        first_word in WEB_TARGETS
        or candidate in WEB_TARGETS
        or first_word in INTERNAL_COMMAND_TARGETS
        or candidate in INTERNAL_COMMAND_TARGETS
    ):
        return None
    if re.search(r"\b(?:canal|video|pesquisa|busca|site)\b", candidate):
        return None

    return candidate


def resolve_target_device(text: str) -> str:
    normalized = normalize_text(text)
    for pattern in TARGET_PATTERNS:
        if re.search(pattern, normalized):
            return "desktop"
    return "desktop"


def _has_action_verb(text: str) -> bool:
    for pattern in VERB_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def detect_desktop_action(text: str) -> DesktopCommand:
    normalized = normalize_text(text)
    app = resolve_app_name(text)
    has_verb = _has_action_verb(normalized)

    if not app and has_verb:
        app = extract_unknown_app_name(text)

    if not app:
        return DesktopCommand()

    confidence = 0.98 if has_verb else 0.85
    label = APP_LABELS.get(app, app)
    return DesktopCommand(
        matched=True,
        intent="desktop",
        command="open_app",
        app=app,
        target_device=resolve_target_device(text),
        confidence=confidence,
        response_message=f"Vou abrir o {label} no seu computador.",
    )


def detect_desktop_command(message: str) -> DesktopCommand:
    return detect_desktop_action(message)
