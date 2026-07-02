import re
from dataclasses import dataclass, field


APP_ALIASES = {
    "notepad": "notepad",
    "bloco de notas": "notepad",
    "bloco": "notepad",
    "bloco notas": "notepad",
    "calculadora": "calculator",
    "calculator": "calculator",
    "calc": "calculator",
    "explorer": "explorer",
    "explorador": "explorer",
    "explorador de arquivos": "explorer",
    "arquivos": "explorer",
    "files": "explorer",
    "vscode": "vscode",
    "vs code": "vscode",
    "visual studio code": "vscode",
    "code": "vscode",
    "discord": "discord",
    "navegador": "browser",
    "browser": "browser",
    "chrome": "chrome",
    "edge": "edge",
    "firefox": "firefox",
    "terminal": "terminal",
    "cmd": "terminal",
    "powershell": "terminal",
}

VERB_PATTERNS = [
    r"abra\b", r"abrir\b", r"abre\b", r"iniciar\b", r"inicia\b",
    r"execute\b", r"roda\b", r"rude\b", r"abra\b", r"abrir\b",
]

TARGET_PATTERNS = [
    r"no\s+meu\s+computador",
    r"no\s+pc",
    r"no\s+computador",
    r"no\s+desktop",
    r"na\s+m[aá]quina",
    r"no\s+meu\s+pc",
]


@dataclass
class DesktopCommand:
    matched: bool = False
    intent: str = ""
    command: str = ""
    app: str = ""
    target_device: str = "desktop"
    confidence: float = 0.0
    response_message: str = ""


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\sàáâãéêíóôõúüç]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _has_verb(text: str) -> bool:
    for pattern in VERB_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def _detect_app(text: str) -> str | None:
    normalized = _normalize(text)
    best_match = None
    best_len = 0
    for alias, app_name in APP_ALIASES.items():
        if alias in normalized:
            if len(alias) > best_len:
                best_len = len(alias)
                best_match = app_name
    return best_match


def _is_target_desktop(text: str) -> bool:
    normalized = _normalize(text)
    for pattern in TARGET_PATTERNS:
        if re.search(pattern, normalized):
            return True
    return False


def detect_desktop_command(message: str) -> DesktopCommand:
    normalized = _normalize(message)
    app = _detect_app(normalized)
    has_verb = _has_verb(normalized)

    if app and has_verb:
        return DesktopCommand(
            matched=True,
            intent="desktop",
            command="open_app",
            app=app,
            target_device="desktop",
            confidence=0.95,
            response_message=f"Vou abrir {_pretty_app_name(app)}.",
        )

    if app and not has_verb:
        return DesktopCommand(
            matched=True,
            intent="desktop",
            command="open_app",
            app=app,
            target_device="desktop",
            confidence=0.85,
            response_message=f"Vou abrir {_pretty_app_name(app)}.",
        )

    return DesktopCommand()


def _pretty_app_name(app: str) -> str:
    names = {
        "notepad": "o Bloco de Notas",
        "calculator": "a Calculadora",
        "explorer": "o Explorer",
        "vscode": "o VS Code",
        "discord": "o Discord",
        "browser": "o navegador",
        "chrome": "o Chrome",
        "edge": "o Edge",
        "firefox": "o Firefox",
        "terminal": "o terminal",
    }
    return names.get(app, app)
