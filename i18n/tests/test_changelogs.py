# i18n/tests/test_changelogs.py
import importlib.util, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CL = os.path.join(ROOT, "i18n", "changelogs")


def _slugs():
    return json.load(open(os.path.join(ROOT, "i18n", "apps", "_index.json")))


def test_changelog_files_exist_and_are_lists():
    for slug in _slugs():
        data = json.load(open(os.path.join(CL, slug + ".json")))
        assert isinstance(data, list)
        for entry in data:
            assert {"version", "date", "notes", "url"} <= set(entry)
            assert len(entry["date"]) == 10 and entry["date"][4] == "-"


def _fetch_module():
    path = os.path.join(ROOT, "scripts", "fetch-changelogs.py")
    spec = importlib.util.spec_from_file_location("fetch_changelogs", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CLEAN = _fetch_module().clean_notes


def test_auto_generated_pr_titles_are_dropped_when_prose_exists():
    """The PR list under "What's Changed" is machine-written and reads badly on a
    marketing page, so prose above it wins."""
    notes = CLEAN(
        "Uninstall moved into Settings.\n"
        "\n"
        "- **Where it is now.** The last pane in the sidebar.\n"
        "\n"
        "## What's Changed\n"
        "* feat: drop Uninstall from the menu by @teddychan in https://x/pull/1\n"
        "\n"
        "**Full Changelog**: https://x/compare/v1...v2\n"
    )
    assert notes == "Uninstall moved into Settings. · Where it is now. The last pane in the sidebar."
    assert "feat: drop Uninstall" not in notes


def test_pr_titles_are_kept_when_there_is_no_prose():
    """Older releases never got a written summary — falling through to the PR
    list beats rendering an empty row."""
    notes = CLEAN(
        "## What's Changed\n"
        "* release: v2.0.4 — fix recording a clashing shortcut by @teddychan in https://x/pull/5\n"
        "\n"
        "**Full Changelog**: https://x/compare/v1...v2\n"
    )
    assert notes == "release: v2.0.4 — fix recording a clashing shortcut"


def test_at_most_four_segments():
    notes = CLEAN("\n\n".join("Paragraph %d." % i for i in range(1, 8)))
    assert len(notes.split(" · ")) == 4


def test_empty_body_is_empty():
    assert CLEAN(None) == "" and CLEAN("") == ""
