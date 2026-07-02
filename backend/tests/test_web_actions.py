import pytest
from app.web_actions.engine import WebActionEngine
from app.web_actions.parser import parse_web_entities
from app.web_actions.url_templates import build_url, KNOWN_SITES


def test_parse_youtube_channel():
    entities = parse_web_entities("abra o canal do alanzoka no YouTube")
    assert entities.target_site == "youtube"
    assert entities.content_type == "channel"
    assert "alanzoka" in entities.creator
    assert entities.action_type == "open_youtube_channel_search"


def test_parse_youtube_video():
    entities = parse_web_entities("abra um vídeo do alanzoka de minecraft")
    assert entities.target_site == "youtube"
    assert entities.content_type == "video"
    assert "alanzoka" in entities.creator
    assert "minecraft" in entities.topic
    assert entities.action_type == "open_youtube_video_search"


def test_parse_youtube_search():
    entities = parse_web_entities("pesquise como instalar mods no YouTube")
    assert entities.target_site == "youtube"
    assert "mods" in entities.query
    assert entities.action_type == "open_youtube_search"


def test_parse_google_search():
    entities = parse_web_entities("pesquise wake on lan no Google")
    assert entities.target_site == "google"
    assert "wake on lan" in entities.query
    assert entities.action_type == "search_google"


def test_parse_github_search():
    entities = parse_web_entities("pesquise misaka network no GitHub")
    assert entities.target_site == "github"
    assert "misaka network" in entities.query
    assert entities.action_type == "search_github"


def test_parse_reddit_search():
    entities = parse_web_entities("pesquise build de minecraft no Reddit")
    assert entities.target_site == "reddit"
    assert "minecraft" in entities.query
    assert entities.action_type == "search_reddit"


def test_parse_curseforge_search():
    entities = parse_web_entities("procure mods no CurseForge")
    assert entities.target_site == "curseforge"
    assert entities.action_type == "search_site"


def test_parse_modrinth_search():
    entities = parse_web_entities("procure cobblemon no Modrinth")
    assert entities.target_site == "modrinth"
    assert "cobblemon" in entities.query
    assert entities.action_type == "search_site"


def test_engine_youtube_channel():
    engine = WebActionEngine()
    action = engine.process("abra o canal do alanzoka no YouTube")
    assert action is not None
    assert action.action_type == "open_youtube_channel_search"
    assert "alanzoka" in action.url
    assert "canal" in action.url
    assert "youtube.com" in action.url


def test_engine_youtube_video():
    engine = WebActionEngine()
    action = engine.process("abra um vídeo do alanzoka de minecraft")
    assert action is not None
    assert action.action_type == "open_youtube_video_search"
    assert "alanzoka" in action.url
    assert "minecraft" in action.url


def test_engine_google_search():
    engine = WebActionEngine()
    action = engine.process("pesquise wake on lan no Google")
    assert action is not None
    assert action.action_type == "search_google"
    assert "google.com" in action.url
    assert "wake" in action.url


def test_engine_github_search():
    engine = WebActionEngine()
    action = engine.process("pesquise misaka network no GitHub")
    assert action is not None
    assert action.action_type == "search_github"
    assert "github.com" in action.url


def test_engine_reddit_search():
    engine = WebActionEngine()
    action = engine.process("pesquise build de minecraft no Reddit")
    assert action is not None
    assert action.action_type == "search_reddit"
    assert "reddit.com" in action.url


def test_engine_modrinth_search():
    engine = WebActionEngine()
    action = engine.process("procure cobblemon no Modrinth")
    assert action is not None
    assert action.action_type == "search_site"
    assert "modrinth.com" in action.url


def test_engine_returns_none_for_conversation():
    engine = WebActionEngine()
    action = engine.process("como vai você?")
    assert action is None


def test_engine_returns_none_for_empty():
    engine = WebActionEngine()
    action = engine.process("")
    assert action is None


def test_build_url_encodes_query():
    url = build_url("https://www.google.com/search?q={query}", "wake on lan")
    assert "wake+on+lan" in url
    assert "google.com" in url


def test_known_sites_has_youtube():
    assert "youtube" in KNOWN_SITES
    assert "search" in KNOWN_SITES["youtube"]["templates"]


def test_known_sites_has_github():
    assert "github" in KNOWN_SITES
    assert "search" in KNOWN_SITES["github"]["templates"]
