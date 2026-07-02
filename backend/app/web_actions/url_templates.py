from urllib.parse import quote_plus


GOOGLE_SEARCH = "https://www.google.com/search?q={query}"
YOUTUBE_SEARCH = "https://www.youtube.com/results?search_query={query}"
YOUTUBE_CHANNEL_SEARCH = "https://www.youtube.com/results?search_query={query}+canal"
YOUTUBE_VIDEO_SEARCH = "https://www.youtube.com/results?search_query={query}+video"
GITHUB_SEARCH = "https://github.com/search?q={query}&type=repositories"
REDDIT_SEARCH = "https://www.reddit.com/search/?q={query}"
WIKIPEDIA_PT = "https://pt.wikipedia.org/w/index.php?search={query}"
DUCKDUCKGO = "https://duckduckgo.com/?q={query}"
GOOGLE_SITE_SEARCH = "https://www.google.com/search?q=site%3A{site}+{query}"
TWITCH_SEARCH = "https://www.twitch.tv/search?term={query}"
STEAM_SEARCH = "https://store.steampowered.com/search/?term={query}"
CURSEFORGE_SEARCH = "https://www.curseforge.com/minecraft/search?search={query}"
MODRINTH_SEARCH = "https://modrinth.com/mods?q={query}"
NEXUSMODS_SEARCH = "https://www.nexusmods.com/search/?gsearch={query}"
GOOGLE_MAPS = "https://www.google.com/maps/search/{query}"


def build_url(template: str, query: str, site: str = "") -> str:
    encoded_query = quote_plus(query)
    encoded_site = quote_plus(site) if site else ""
    if "{site}" in template:
        return template.format(query=encoded_query, site=encoded_site)
    return template.format(query=encoded_query)


KNOWN_SITES = {
    "youtube": {
        "domains": ["youtube.com", "youtu.be"],
        "templates": {
            "search": YOUTUBE_SEARCH,
            "channel": YOUTUBE_CHANNEL_SEARCH,
            "video": YOUTUBE_VIDEO_SEARCH,
        },
    },
    "google": {
        "domains": ["google.com"],
        "templates": {"search": GOOGLE_SEARCH},
    },
    "github": {
        "domains": ["github.com"],
        "templates": {"search": GITHUB_SEARCH},
    },
    "reddit": {
        "domains": ["reddit.com"],
        "templates": {"search": REDDIT_SEARCH},
    },
    "wikipedia": {
        "domains": ["wikipedia.org"],
        "templates": {"search": WIKIPEDIA_PT},
    },
    "twitch": {
        "domains": ["twitch.tv"],
        "templates": {"search": TWITCH_SEARCH},
    },
    "steam": {
        "domains": ["store.steampowered.com", "steampowered.com"],
        "templates": {"search": STEAM_SEARCH},
    },
    "curseforge": {
        "domains": ["curseforge.com"],
        "templates": {"search": CURSEFORGE_SEARCH},
    },
    "modrinth": {
        "domains": ["modrinth.com"],
        "templates": {"search": MODRINTH_SEARCH},
    },
    "nexusmods": {
        "domains": ["nexusmods.com"],
        "templates": {"search": NEXUSMODS_SEARCH},
    },
}


def get_site_by_domain(domain: str) -> str | None:
    lower = domain.lower()
    for site_name, site_info in KNOWN_SITES.items():
        for d in site_info["domains"]:
            if d in lower:
                return site_name
    return None
