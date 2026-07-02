from dataclasses import dataclass, field


@dataclass
class Intent:
    name: str
    confidence: float = 1.0
    tool_name: str | None = None
    requires_confirmation: bool = False
    response_message: str = ""
    parameters: dict = field(default_factory=dict)


INTENT_MAP = {
    "clear_alerts": {
        "keywords": [
            "limpe os alertas", "limpar alertas", "marque os alertas como vistos",
            "marcar alertas como vistos", "apague os alertas", "limpe notificações",
            "marcar notificações como vistas", "limpe notificações importantes"
        ],
        "tool_name": "notifications.ack_all_alerts",
        "requires_confirmation": False,
        "response_message": "Marquei todos os alertas atuais como vistos, diz Misaka Misaka."
    },
    "clear_resolved": {
        "keywords": [
            "apague os alertas resolvidos", "deletar alertas resolvidos",
            "limpe alertas resolvidos", "remover alertas antigos"
        ],
        "tool_name": "notifications.clear_resolved_alerts",
        "requires_confirmation": True,
        "response_message": "Vou limpar os alertas resolvidos, mas isso deleta dados. Confirme?"
    },
    "show_alerts": {
        "keywords": [
            "mostrar alertas", "quais notificações", "tem algo importante",
            "mostre os alertas", "ver alertas", "lista de alertas"
        ],
        "tool_name": "notifications.list_alerts",
        "requires_confirmation": False,
        "response_message": ""
    },
    "hud_on": {
        "keywords": [
            "ative o modo hud", "ative hud", "ligue o hud", "modo hud ligado",
            "ativar modo hud", "ativa hud"
        ],
        "tool_name": "ui.set_hud_mode",
        "parameters": {"enabled": True},
        "requires_confirmation": False,
        "response_message": "Modo HUD ativado, diz Misaka Misaka."
    },
    "hud_off": {
        "keywords": [
            "desative o modo hud", "desative hud", "desligue o hud", "modo hud desligado",
            "desativar modo hud", "desativa hud"
        ],
        "tool_name": "ui.set_hud_mode",
        "parameters": {"enabled": False},
        "requires_confirmation": False,
        "response_message": "Modo HUD desativado, diz Misaka Misaka."
    },
    "open_settings": {
        "keywords": [
            "abra configurações", "abrir configurações", "mostrar configurações",
            "configurações", "abra as configs"
        ],
        "tool_name": "ui.open_settings",
        "requires_confirmation": False,
        "response_message": "Abrindo configurações, diz Misaka Misaka."
    },
    "clear_chat": {
        "keywords": [
            "limpe o chat", "limpar chat", "limpe a conversa", "limpar conversa",
            "resetar chat", "reiniciar chat", "limpe o bate-papo"
        ],
        "tool_name": "ui.clear_chat",
        "requires_confirmation": False,
        "response_message": "Chat limpo, diz Misaka Misaka."
    },
    "voice_on": {
        "keywords": [
            "ligue a voz", "ative a voz", "ativar voz", "ligar voz",
            "ative voz", "liga a voz"
        ],
        "tool_name": "ui.set_voice_enabled",
        "parameters": {"enabled": True},
        "requires_confirmation": False,
        "response_message": "Voz ativada, diz Misaka Misaka."
    },
    "voice_off": {
        "keywords": [
            "desligue a voz", "desative a voz", "desativar voz", "desligar voz",
            "desative voz", "desliga a voz"
        ],
        "tool_name": "ui.set_voice_enabled",
        "parameters": {"enabled": False},
        "requires_confirmation": False,
        "response_message": "Voz desativada, diz Misaka Misaka."
    },
    "voice_female": {
        "keywords": [
            "mude para voz feminina", "voz feminina", "mudar voz feminina",
            "usar voz feminina", "trocar para voz feminina"
        ],
        "tool_name": "ui.set_voice_profile",
        "parameters": {"profile": "feminine"},
        "requires_confirmation": False,
        "response_message": "Perfil de voz feminina selecionado, diz Misaka Misaka."
    },
    "search_youtube": {
        "keywords": [
            "pesquise no youtube", "buscar no youtube", "procure no youtube",
            "youtube pesquisar", "canal do", "canal da", "canal de",
            "abrir canal"
        ],
        "tool_name": "desktop.search_web",
        "requires_confirmation": False,
        "response_message": ""
    },
    "open_youtube": {
        "keywords": [
            "abra o youtube", "abrir youtube", "abre o youtube",
            "youtube", "abra youtube"
        ],
        "tool_name": "desktop.open_url",
        "parameters": {"url": "https://www.youtube.com"},
        "requires_confirmation": False,
        "response_message": "Abrindo YouTube, diz Misaka Misaka."
    },
    "open_url_site": {
        "keywords": [
            "abra o google", "abra o github", "abra o site",
            "abra a página", "abra o gmail", "abra o maps",
            "abra o drive", "abra o notion", "abra o figma"
        ],
        "tool_name": "desktop.open_url",
        "requires_confirmation": False,
        "response_message": ""
    },
    "open_app": {
        "keywords": [
            "abra o discord", "abra o vscode", "abra o vs code",
            "abra o explorer", "abra o notepad", "abra o terminal",
            "abra o calculador", "abra o bloco de notas",
            "abra o music", "abra o spotify"
        ],
        "tool_name": "desktop.open_app",
        "requires_confirmation": False,
        "response_message": ""
    },
    "open_browser": {
        "keywords": [
            "abra o navegador", "abrir navegador", "abre o chrome",
            "abra o chrome", "abra o firefox", "abra o edge",
            "abra o navegador padrão"
        ],
        "tool_name": "desktop.open_app",
        "parameters": {"app": "browser"},
        "requires_confirmation": False,
        "response_message": "Abrindo navegador, diz Misaka Misaka."
    },
    "search_web": {
        "keywords": [
            "pesquise por", "pesquisar", "procure por", "procure no google",
            "busque por", "buscar no google"
        ],
        "tool_name": "desktop.search_web",
        "requires_confirmation": False,
        "response_message": ""
    },
    "pc_status": {
        "keywords": [
            "qual o status do meu pc", "status do computador", "status do sistema",
            "informações do pc", "como está o pc"
        ],
        "tool_name": "desktop.get_system_status",
        "requires_confirmation": False,
        "response_message": ""
    },
    "android_vibrate": {
        "keywords": [
            "faça meu celular vibrar", "vibrar celular", "mande vibrar",
            "faz o celular vibrar", "vibração no celular"
        ],
        "tool_name": "android.vibrate",
        "requires_confirmation": False,
        "response_message": "Comando de vibração enviado ao celular, diz Misaka Misaka."
    },
    "android_open_app": {
        "keywords": [
            "abra o youtube no celular", "abra o whatsapp no celular",
            "abra o instagram no celular", "abra o app no celular"
        ],
        "tool_name": "android.open_app",
        "requires_confirmation": False,
        "response_message": ""
    },
    "android_toast": {
        "keywords": [
            "mande um alerta no celular", "mostre alerta no celular",
            "envie um toast", "mande um toast pro celular"
        ],
        "tool_name": "android.show_toast",
        "requires_confirmation": False,
        "response_message": "Alerta enviado ao celular, diz Misaka Misaka."
    },
    "android_status": {
        "keywords": [
            "mostre notificações do celular", "notificações do celular",
            "status do celular", "ações pendentes do celular"
        ],
        "tool_name": "android.list_pending_actions",
        "requires_confirmation": False,
        "response_message": ""
    },
    "create_task": {
        "keywords": [
            "crie uma tarefa", "criar tarefa", "nova tarefa",
            "adicione uma tarefa", "adicionar tarefa"
        ],
        "tool_name": "tasks.create",
        "requires_confirmation": False,
        "response_message": ""
    },
    "list_tasks": {
        "keywords": [
            "liste minhas tarefas", "listar tarefas", "quais tarefas",
            "mostre as tarefas", "ver tarefas", "o que tenho pendente"
        ],
        "tool_name": "tasks.list",
        "requires_confirmation": False,
        "response_message": ""
    },
    "complete_task": {
        "keywords": [
            "marque tarefa como concluída", "concluir tarefa",
            "marcar como feita", "tarefa concluída"
        ],
        "tool_name": "tasks.complete",
        "requires_confirmation": False,
        "response_message": ""
    },
    "remember": {
        "keywords": [
            "lembre que", "salve isso na memória", "guarde isso",
            "lembre-se de", "anote que"
        ],
        "tool_name": "memory.create",
        "requires_confirmation": False,
        "response_message": ""
    },
    "recall": {
        "keywords": [
            "o que você lembra", "o que lembra sobre", "lembra de mim",
            "o que sabe sobre", "quais memórias"
        ],
        "tool_name": "memory.search",
        "requires_confirmation": False,
        "response_message": ""
    },
    "forget": {
        "keywords": [
            "esqueça isso", "apague essa memória", "delete essa memória",
            "esqueça sobre", "remova essa memória"
        ],
        "tool_name": "memory.delete",
        "requires_confirmation": True,
        "response_message": "Tem certeza que deseja apagar essa memória?"
    },
    "create_reminder": {
        "keywords": [
            "me lembre de", "crie um lembrete", "lembrar de",
            "criar lembrete", "agendar lembrete"
        ],
        "tool_name": "reminders.create",
        "requires_confirmation": False,
        "response_message": ""
    },
    "list_reminders": {
        "keywords": [
            "liste lembretes", "quais lembretes", "mostre lembretes",
            "ver lembretes", "meus lembretes"
        ],
        "tool_name": "reminders.list",
        "requires_confirmation": False,
        "response_message": ""
    }
}
