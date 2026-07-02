import json
import os


def test_desktop_package_json_exists():
    pkg_path = os.path.join(os.path.dirname(__file__), '..', '..', 'desktop', 'package.json')
    assert os.path.exists(pkg_path), "desktop/package.json not found"


def test_desktop_package_has_extra_resources():
    pkg_path = os.path.join(os.path.dirname(__file__), '..', '..', 'desktop', 'package.json')
    with open(pkg_path) as f:
        pkg = json.load(f)
    build = pkg.get("build", {})
    extra = build.get("extraResources", [])
    assert len(extra) > 0, "No extraResources configured for dashboard"
    dashboard_found = any(
        r.get("to") == "dashboard" for r in extra
    )
    assert dashboard_found, "Dashboard not included in extraResources"


def test_desktop_package_has_main_files():
    pkg_path = os.path.join(os.path.dirname(__file__), '..', '..', 'desktop', 'package.json')
    with open(pkg_path) as f:
        pkg = json.load(f)
    build = pkg.get("build", {})
    files = build.get("files", [])
    assert "main.js" in files
    assert "preload.js" in files
    assert "package.json" in files


def test_desktop_package_has_nsis_config():
    pkg_path = os.path.join(os.path.dirname(__file__), '..', '..', 'desktop', 'package.json')
    with open(pkg_path) as f:
        pkg = json.load(f)
    build = pkg.get("build", {})
    assert "nsis" in build
    assert build["nsis"]["oneClick"] is False
