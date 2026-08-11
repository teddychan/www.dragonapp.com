# i18n/tests/test_changelogs.py
#
# The changelog rows are the app's own What's New pane, transported by
# scripts/fetch-changelogs.py from each release's `whats-new.json` asset and
# rendered per locale by i18n/build_i18n.py. Two things these tests exist to
# stop, both of which shipped:
#
#   * English notes under a localized heading — `notes` was one string, so
#     docs/ja/spectacle-2/index.html rendered English under 「新着情報」.
#   * The GitHub Release body reaching the site — those bodies are generated
#     from PR titles ("docs: realign RELEASING.md with the actual release
#     workflow"), which is not marketing copy in any language.
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CL = os.path.join(ROOT, "i18n", "changelogs")
STRINGS = os.path.join(ROOT, "i18n", "strings")
LANGS = ["en-US", "zh-Hans", "zh-Hant", "ja", "ko", "es", "fr"]


def _module(relpath, name):
    path = os.path.join(ROOT, relpath)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FETCH = _module(os.path.join("scripts", "fetch-changelogs.py"), "fetch_changelogs")
BUILD = _module(os.path.join("i18n", "build_i18n.py"), "build_i18n")


def _slugs():
    return json.load(open(os.path.join(ROOT, "i18n", "apps", "_index.json")))


def _asset(name="whats-new.json"):
    return {"name": name, "browser_download_url": "https://x/%s" % name}


def _release(tag, assets=(), body="", date="2026-08-11T09:00:00Z"):
    return {"tag_name": tag, "published_at": date, "body": body,
            "html_url": "https://github.com/teddychan/spectacle-2/releases/tag/" + tag,
            "assets": list(assets), "draft": False, "prerelease": False}


def _never(asset):
    raise AssertionError("no asset should have been downloaded: %r" % (asset,))


def _doc(version="2.5.4", languages=None, default="en", schema=1):
    return json.dumps({
        "schema": schema, "app": "spectacle-2", "version": version,
        "date": "2026-08-11", "default_language": default,
        "languages": languages if languages is not None else {
            "en": {"summary": "Window snapping is steadier.",
                   "sections": [{"kind": "fixed", "entries": ["Halves no longer drift."]}]},
            "ja": {"summary": "ウインドウの整列が安定しました。",
                   "sections": [{"kind": "fixed", "entries": ["左右半分がずれなくなりました。"]}]},
        },
    }, ensure_ascii=False)


# ---------------------------------------------------------------- the transport

def test_notes_are_read_from_the_whats_new_asset():
    out = FETCH.merge_entries([_release("v2.5.4", assets=[_asset()])], [],
                              lambda a: _doc())
    assert out[0]["version"] == "2.5.4"
    assert out[0]["notes"]["ja"] == "ウインドウの整列が安定しました。 · 左右半分がずれなくなりました。"
    # The release date, not the asset's `date`: the row says when the version shipped.
    assert out[0]["date"] == "2026-08-11"


def test_section_and_entry_order_is_the_apps_order():
    """`kind` order is the app's render order — not alphabetical, not the enum's."""
    notes = FETCH.parse_whats_new(_doc(languages={"en": {
        "summary": "S",
        "sections": [{"kind": "fixed", "entries": ["F1", "F2"]},
                     {"kind": "security", "entries": ["Sec"]},
                     {"kind": "added", "entries": ["A1"]}],
    }}), "2.5.4")
    assert notes["en"] == "S · F1 · F2 · Sec · A1"


def test_release_without_the_asset_keeps_the_entry_the_site_has():
    """No backfill: every release published so far predates the asset.

    A release with no asset and no existing entry contributes nothing — the four
    newest releases will have no site row until each app's next release, which is
    accepted. What must never happen is the existing rows changing.
    """
    existing = [{"version": "2.5.3", "date": "2026-08-11",
                 "notes": {"en": "Already published."},
                 "url": "https://github.com/teddychan/spectacle-2/releases/tag/v2.5.3"}]
    out = FETCH.merge_entries([_release("v2.5.4"), _release("v2.5.3")], existing, _never)
    assert out == existing


def test_the_release_body_is_never_rendered():
    body = ("## What's Changed\n"
            "* docs: realign RELEASING.md with the actual release workflow by @teddychan\n")
    assert FETCH.merge_entries([_release("v2.5.4", body=body)], [], _never) == []


@pytest.mark.parametrize("raw", [
    b"<html>404</html>",                        # the download served something else
    None,                                       # the download failed
    _doc(schema=2),                             # a shape this script cannot read
    _doc(version="2.5.3"),                      # a stale or foreign artifact
    _doc(languages={}),                         # nothing to say
])
def test_an_unusable_asset_keeps_the_existing_entry(raw):
    existing = [{"version": "2.5.4", "date": "2026-08-10",
                 "notes": {"en": "Already published."}, "url": "https://x"}]
    out = FETCH.merge_entries([_release("v2.5.4", assets=[_asset()])], existing,
                              lambda a: raw)
    assert out == existing


def test_a_version_stated_with_a_v_still_matches_its_tag():
    assert FETCH.parse_whats_new(_doc(version="v2.5.4"), "2.5.4")


def test_default_language_supplies_the_sites_fallback():
    """The asset's own rule — a missing language renders `default_language`."""
    notes = FETCH.parse_whats_new(_doc(default="ja", languages={
        "ja": {"summary": "日本語のみ", "sections": []}}), "2.5.4")
    assert notes["en"] == "日本語のみ"


def test_entries_older_than_the_api_window_are_kept():
    existing = [{"version": "2.5.3", "date": "2026-08-11", "notes": {"en": "newer"},
                 "url": "https://x"},
                {"version": "2.2.2", "date": "2026-08-07", "notes": {"en": "aged out"},
                 "url": "https://y"}]
    out = FETCH.merge_entries([_release("v2.5.3")], existing, _never)
    assert [e["version"] for e in out] == ["2.5.3", "2.2.2"]


def test_only_exact_public_tags_reach_the_changelog():
    releases = [_release("mas-v2.20.1", assets=[_asset()]),
                _release("v2.5.1-beta1", assets=[_asset()]),
                _release("sample-v1.4.0", assets=[_asset()])]
    assert FETCH.merge_entries(releases, [], _never) == []


def test_a_refresh_with_no_assets_anywhere_changes_nothing():
    """The idempotency invariant, on the real committed data.

    No app has published a `whats-new.json` yet, so a refresh must be a no-op on
    content. If this ever fails, `python3 scripts/fetch-changelogs.py` is about to
    blank or delete the live changelogs of four apps.
    """
    for slug in _slugs():
        existing = json.load(open(os.path.join(CL, slug + ".json")))
        # Newest first, plus one release newer than anything on file — the state
        # the four apps are in right now.
        releases = [_release("v9.9.9")] + [_release("v" + e["version"]) for e in existing]
        assert FETCH.merge_entries(releases, existing, _never) == existing, slug


# ------------------------------------------------------------------- the render

ENTRY = {"version": "2.5.4", "date": "2026-08-11", "url": "https://x",
         "notes": {"en": "Window snapping is steadier.",
                   "ja": "ウインドウの整列が安定しました。"}}


def _rows(monkeypatch, entry, lang):
    monkeypatch.setattr(BUILD, "load_changelog", lambda slug: [entry])
    return BUILD.render_changelog_rows("spectacle-2", {"app_changelog_view": "View"}, lang)


def test_a_page_renders_its_own_locale(monkeypatch):
    html = _rows(monkeypatch, ENTRY, "ja")
    assert "ウインドウの整列が安定しました。" in html
    assert "Window snapping is steadier." not in html


def test_a_locale_the_app_skips_falls_back_to_english(monkeypatch):
    for lang in ["ko", "es", "fr", "zh-Hans", "zh-Hant"]:
        assert "Window snapping is steadier." in _rows(monkeypatch, ENTRY, lang), lang


def test_the_english_page_reads_the_apps_en_notes(monkeypatch):
    """The site says en-US; every app ships `en`. That mapping is the whole gap."""
    assert "Window snapping is steadier." in _rows(monkeypatch, ENTRY, "en-US")


def test_an_english_only_app_renders_everywhere(monkeypatch):
    """ice-2 localizes with String Catalogs and publishes English only."""
    entry = dict(ENTRY, notes={"en": "Ice 2 idles quieter."})
    for lang in LANGS:
        assert "Ice 2 idles quieter." in _rows(monkeypatch, entry, lang), lang


def test_pre_language_string_notes_still_render(monkeypatch):
    """Entries written before `notes` gained languages were English by definition."""
    entry = dict(ENTRY, notes="A maintenance release.")
    assert "A maintenance release." in _rows(monkeypatch, entry, "ja")


# --------------------------------------------------------------------- the data

def test_changelog_files_exist_and_carry_a_language_dimension():
    """The migration: `notes` is {lang: line}, never one language's bare string."""
    for slug in _slugs():
        data = json.load(open(os.path.join(CL, slug + ".json")))
        assert isinstance(data, list)
        for entry in data:
            assert {"version", "date", "notes", "url"} <= set(entry)
            assert len(entry["date"]) == 10 and entry["date"][4] == "-"
            assert isinstance(entry["notes"], dict), (slug, entry["version"])
            # English is what every locale falls back to, so it has to be there.
            assert entry["notes"].get("en"), (slug, entry["version"])


def test_every_locale_names_the_notes_source_truthfully():
    """`app_changelog_auto` said "Auto-generated from GitHub Releases".

    That became false the moment the notes came from the app's What's New pane,
    so the key was renamed and retranslated in all seven tables. Asserting the
    old key is gone matters as much as the new one being present: a table that
    kept it would keep rendering the claim.
    """
    for lang in LANGS:
        common = json.load(open(os.path.join(STRINGS, lang + ".json")))["common"]
        assert "app_changelog_auto" not in common, lang
        caption = common.get("app_changelog_source")
        assert caption, lang
        assert "GitHub" not in caption, (lang, caption)
