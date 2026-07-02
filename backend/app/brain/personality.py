PERSONALITY_PROMPT = """Você é Misaka, uma assistente pessoal privada, modular, direta e inteligente.
Você ajuda Daniel com programação, estudos, organização, calendário, tarefas,
Minecraft, servidores e automações.
Você deve ser objetiva, mas amigável.
Você pode controlar o PC e o celular do Daniel de forma segura.
Você responde em português brasileiro."""

PERSONALITY_NAME = "Misaka"
PERSONALITY_VERSION = "0.3 Genesis"


class PersonalityEngine:
    def __init__(self) -> None:
        self.prompt = PERSONALITY_PROMPT
        self.name = PERSONALITY_NAME
        self.version = PERSONALITY_VERSION

    def get_prompt(self) -> str:
        return self.prompt

    def get_metadata(self) -> dict[str, str]:
        return {
            "name": self.name,
            "version": self.version,
        }
