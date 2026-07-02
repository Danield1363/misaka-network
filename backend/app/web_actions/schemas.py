from dataclasses import dataclass, field


@dataclass
class WebAction:
    action_type: str
    url: str
    target: str = "desktop"
    query: str = ""
    site: str = ""
    source: str = "web_action_engine"
    response_message: str = ""


@dataclass
class ParsedEntities:
    target_site: str = ""
    query: str = ""
    content_type: str = ""
    creator: str = ""
    topic: str = ""
    device_target: str = "desktop"
    action_type: str = ""
    raw_message: str = ""
