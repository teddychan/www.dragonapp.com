# AGENTS.md

Source for www.dragonapp.com, the Dragon App marketing site, generated from `i18n/` into `docs/` and served by GitHub Pages. Editing, build and publish order are in [README.md](README.md).

## Project rules

- Run the tests before the build, never after. `i18n/tests/test_build.py` runs `i18n/build_i18n.py` against the live `docs/` tree, which writes asset URLs bare and strips the `?v=` fingerprints. Order: test, build, `scripts/cache-bust.sh`, and nothing touches `docs/` after cache-bust. Never chain `pytest && git add -A`.
- Before committing, check the fingerprints survived: `grep -rl '?v=' docs --include='*.html' | wc -l` must match the count on `origin/main`, not drop to 0. When verifying someone else's branch, judge fingerprints from committed content (`git show <ref>:docs/<page>` or `git diff origin/main <branch> -- 'docs/**/*.html'`), not from a tree pytest has run in; run `git checkout -- docs/` before reusing such a tree.
- A page that exists only in English, such as the hand-written `docs/<slug>/licenses/` notices pages, must not load the i18n runtime (`/shared/i18n.js` or the inlined `{{ INLINE_I18N_JS }}`) or the language switcher. Its `maybeRedirect()` sends non-English visitors to `/<lang>/<same-path>` without checking that the page exists, so they get a 404 that never shows up in an English browser. Either ship all seven locales or drop the runtime.
