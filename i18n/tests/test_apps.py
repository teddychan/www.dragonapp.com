# i18n/tests/test_apps.py
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPS = os.path.join(ROOT, "i18n", "apps")

REQUIRED = {"slug", "name", "theme", "repo", "homebrew_cask", "mas_url",
            "license", "license_url", "min_macos", "appcast_path",
            "credit_name", "credit_url", "sponsors_url"}

def test_index_lists_apps():
    idx = json.load(open(os.path.join(APPS, "_index.json")))
    assert idx == ["ice-2", "clipmenu-2", "yahoo-keykey-2", "spectacle-2"]

def test_each_app_has_required_fields():
    idx = json.load(open(os.path.join(APPS, "_index.json")))
    for slug in idx:
        data = json.load(open(os.path.join(APPS, slug + ".json")))
        assert REQUIRED <= set(data), "%s missing %s" % (slug, REQUIRED - set(data))
        assert data["slug"] == slug
