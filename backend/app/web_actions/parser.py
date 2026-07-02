import re
from app.web_actions.schemas import ParsedEntities


def parse_web_entities(message: str) -> ParsedEntities:
    lower = message.lower().strip()
    entities = ParsedEntities(raw_message=message)

    site_patterns = [
        (r"no\s+youtube|no\s+yt|no\s+ytb", "youtube"),
        (r"no\s+google", "google"),
        (r"no\s+github", "github"),
        (r"no\s+reddit", "reddit"),
        (r"no\s+wikipedia|na\s+wikipédia", "wikipedia"),
        (r"no\s+twitch", "twitch"),
        (r"no\s+steam", "steam"),
        (r"no\s+curseforge", "curseforge"),
        (r"no\s+modrinth", "modrinth"),
        (r"no\s+nexusmods|no\s+nexus", "nexusmods"),
        (r"no\s+google\s+maps", "google_maps"),
    ]
    for pattern, site in site_patterns:
        if re.search(pattern, lower):
            entities.target_site = site
            break

    if not entities.target_site:
        if re.search(r"\b(?:abra|abrir|abre)\s+(?:o\s+)?(?:site\s+do\s+)?youtube\b", lower):
            entities.target_site = "youtube"
            entities.action_type = "open_youtube_home"
        elif re.search(r"\b(?:abra|abrir|abre)\s+(?:o\s+)?google\b", lower):
            entities.target_site = "google"
            entities.action_type = "open_google_home"

    content_patterns = [
        (r"canal\s+(?:do|da|de)\s+(.+?)(?:\s+no\s+|\s*$)", "channel"),
        (r"vídeo\s+(?:do|da|de)\s+(.+?)(?:\s+de\s+|\s+no\s+|\s*$)", "video"),
        (r"vídeo\s+de\s+(.+?)(?:\s+no\s+|\s*$)", "video"),
        (r"música\s+(.+?)(?:\s+no\s+|\s*$)", "music"),
        (r"playlist\s+(.+?)(?:\s+no\s+|\s*$)", "playlist"),
    ]
    for pattern, content_type in content_patterns:
        match = re.search(pattern, lower)
        if match:
            entities.content_type = content_type
            entities.creator = match.group(1).strip()
            break

    if entities.content_type in ("channel", "video", "music", "playlist") and not entities.target_site:
        entities.target_site = "youtube"

    topic_patterns = [
        (r"de\s+(?:sobre\s+)?(.+?)(?:\s+no\s+|\s*$)", None),
    ]
    if not entities.topic:
        for pattern, _ in topic_patterns:
            match = re.search(pattern, lower)
            if match:
                candidate = match.group(1).strip()
                if len(candidate) > 2 and candidate not in ("youtube", "google", "github"):
                    entities.topic = candidate
                    break

    query = _extract_query(lower, entities)
    entities.query = query

    if not entities.action_type:
        entities.action_type = _determine_action_type(lower, entities)

    return entities


def _extract_query(lower: str, entities: ParsedEntities) -> str:
    if entities.creator and entities.topic:
        return f"{entities.creator} {entities.topic}"
    if entities.creator:
        suffix = " canal" if entities.content_type == "channel" else ""
        return f"{entities.creator}{suffix}"
    if entities.topic:
        return entities.topic

    query_patterns = [
        r"pesquisar\s+(?:no\s+\w+\s+)?(?:por\s+)?(.+?)(?:\s+no\s+|\s*$)",
        r"pesquise\s+(?:no\s+\w+\s+)?(?:por\s+)?(.+?)(?:\s+no\s+|\s*$)",
        r"procure\s+(?:no\s+\w+\s+)?(?:por\s+)?(.+?)(?:\s+no\s+|\s*$)",
        r"busque\s+(?:no\s+\w+\s+)?(?:por\s+)?(.+?)(?:\s+no\s+|\s*$)",
        r"buscar\s+(?:no\s+\w+\s+)?(?:por\s+)?(.+?)(?:\s+no\s+|\s*$)",
    ]
    for pattern in query_patterns:
        match = re.search(pattern, lower)
        if match:
            return match.group(1).strip()

    return ""


def _determine_action_type(lower: str, entities: ParsedEntities) -> str:
    if re.search(r"canal\s+(?:do|da|de)", lower):
        return "open_youtube_channel_search"
    if re.search(r"vídeo|video", lower):
        return "open_youtube_video_search"
    if re.search(r"música|musica", lower):
        return "open_youtube_video_search"

    if entities.target_site == "youtube":
        return "open_youtube_search"
    if entities.target_site == "google":
        return "search_google"
    if entities.target_site == "github":
        return "search_github"
    if entities.target_site == "reddit":
        return "search_reddit"
    if entities.target_site == "wikipedia":
        return "search_wikipedia"
    if entities.target_site in ("curseforge", "modrinth", "nexusmods", "steam", "twitch"):
        return "search_site"
    if entities.target_site:
        return "search_site"

    return "search_web"
