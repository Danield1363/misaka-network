import logging
from typing import Any

from app.web_actions.parser import parse_web_entities
from app.web_actions.schemas import ParsedEntities, WebAction
from app.web_actions.url_templates import (
    GITHUB_SEARCH,
    GOOGLE_SEARCH,
    GOOGLE_SITE_SEARCH,
    KNOWN_SITES,
    REDDIT_SEARCH,
    WIKIPEDIA_PT,
    YOUTUBE_CHANNEL_SEARCH,
    YOUTUBE_SEARCH,
    YOUTUBE_VIDEO_SEARCH,
    build_url,
)

logger = logging.getLogger(__name__)

ACTION_RESPONSES = {
    "open_youtube_home": "Vou abrir o YouTube.",
    "open_google_home": "Vou abrir o Google.",
    "open_youtube_channel_search": "Vou abrir a busca do canal no YouTube.",
    "open_youtube_video_search": "Vou abrir a busca no YouTube.",
    "open_youtube_search": "Vou pesquisar no YouTube.",
    "search_google": "Vou pesquisar no Google.",
    "search_github": "Vou pesquisar no GitHub.",
    "search_reddit": "Vou pesquisar no Reddit.",
    "search_wikipedia": "Vou pesquisar na Wikipedia.",
    "search_site": "Vou pesquisar no site.",
    "search_web": "Vou pesquisar na web.",
}


class WebActionEngine:
    def __init__(self) -> None:
        self.session_context: dict[str, Any] = {
            "last_site": "",
            "last_query": "",
            "last_action_type": "",
        }

    def process(self, message: str) -> WebAction | None:
        entities = parse_web_entities(message)

        if not entities.query and not entities.action_type:
            return None

        if entities.action_type == "open_youtube_channel_search" and not entities.query:
            return None

        url = self._build_url(entities)
        if not url:
            return None

        response = ACTION_RESPONSES.get(entities.action_type, "Acao pronta.")

        self.session_context["last_site"] = entities.target_site
        self.session_context["last_query"] = entities.query
        self.session_context["last_action_type"] = entities.action_type

        action = WebAction(
            action_type=entities.action_type,
            url=url,
            target=entities.device_target,
            query=entities.query,
            site=entities.target_site,
            response_message=response,
        )

        logger.info(f"Web action: {action.action_type} -> {action.url}")
        return action

    def _build_url(self, entities: ParsedEntities) -> str | None:
        action = entities.action_type
        query = entities.query

        if action == "open_youtube_home":
            return "https://www.youtube.com"
        if action == "open_google_home":
            return "https://www.google.com"

        if not query:
            return None

        if action == "open_youtube_channel_search":
            return build_url(YOUTUBE_CHANNEL_SEARCH, query)
        if action == "open_youtube_video_search":
            return build_url(YOUTUBE_VIDEO_SEARCH, query)
        if action == "open_youtube_search":
            return build_url(YOUTUBE_SEARCH, query)
        if action == "search_google":
            return build_url(GOOGLE_SEARCH, query)
        if action == "search_github":
            return build_url(GITHUB_SEARCH, query)
        if action == "search_reddit":
            return build_url(REDDIT_SEARCH, query)
        if action == "search_wikipedia":
            return build_url(WIKIPEDIA_PT, query)
        if action == "search_site":
            site_info = KNOWN_SITES.get(entities.target_site)
            if site_info and "search" in site_info["templates"]:
                return build_url(site_info["templates"]["search"], query)
            domain = (
                entities.target_site
                if "." in entities.target_site
                else f"{entities.target_site}.com"
            )
            return build_url(GOOGLE_SITE_SEARCH, query, site=domain)

        return build_url(GOOGLE_SEARCH, query)
