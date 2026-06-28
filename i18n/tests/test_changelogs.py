# i18n/tests/test_changelogs.py
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CL = os.path.join(ROOT, "i18n", "changelogs")

def test_changelog_files_exist_and_are_lists():
    for slug in ["ice-2", "clipmenu-2", "yahoo-keykey-2"]:
        data = json.load(open(os.path.join(CL, slug + ".json")))
        assert isinstance(data, list)
        for entry in data:
            assert {"version", "date", "notes", "url"} <= set(entry)
            assert len(entry["date"]) == 10 and entry["date"][4] == "-"
