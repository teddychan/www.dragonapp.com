# i18n/tests/test_build.py
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_build():
    return subprocess.run(
        [sys.executable, "i18n/build_i18n.py"],
        cwd=ROOT, capture_output=True, text=True
    )

def test_build_runs_clean():
    r = run_build()
    assert r.returncode == 0, r.stderr
    assert "Built" in r.stdout
    assert "Traceback" not in r.stderr

def test_known_pages_exist():
    run_build()
    for rel in ["docs/index.html", "docs/zh-Hant/index.html", "docs/support.html"]:
        assert os.path.exists(os.path.join(ROOT, rel)), rel
