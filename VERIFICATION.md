# Verification report - 12 September 2026

## Important boundary

**This is not a certificate of a successful Hugo build or live deployment.**
The package-creation environment did not have Hugo installed and could not
download the official executable. Its browser also could not navigate to a
local HTTP server. No environment policy was changed to bypass these limits.

Therefore, actual Hugo 0.166.0 builds, actual GitHub Actions execution, GitHub
account permissions, real HTTP navigation, browser storage persistence, and
live Pages hosting were **not verified here**.

What was executed is described precisely below. The supplied workflow performs
actual Hugo builds and normal HTTP browser checks on GitHub before deployment.
Those CI checks are included but were not run during package creation.

## Local verification pass 1 - root site URL

Configuration: `http://127.0.0.1:8765/` used as a synthetic base URL.

- Parsed TOML site configuration, both JSON data files, and all Markdown front
  matter. Confirmed six post files, required layouts, artwork, and one workflow.
- Parsed workflow YAML and syntax-checked all six shell command blocks.
  Checked the build/deploy dependency and the `./public` artifact path.
- `node --check` passed for the actual site JavaScript.
- Parsed 22 original site template files with Go's standard template engine;
  rendered 22 page fixtures using the unmodified templates and fixture data.
- Checked **528 local link/asset references**, **44 asset integrity references**,
  six search records, duplicate HTML IDs, TOC fragments, required output paths,
  and fixture XML/JSON validity. All passed.
- Ran **37 Chromium UI/layout assertions** against those rendered fixtures,
  with the site's actual CSS and JavaScript. All passed.

**Fixture specifics:** the test harness supplies Hugo-like page objects and
helper functions. Markdown and built-in feed/sitemap output are fixture
representations, not Hugo's Goldmark or built-in generators. Asset integrity
checks validate the fixture assets, not Hugo's actual minified output. These
checks catch many template, link, and interface mistakes but do not establish
Hugo-specific compatibility.

## Local verification pass 2 - project site URL

Configuration: `http://127.0.0.1:8766/prashantdivate/` used as a synthetic base.

The source was packaged and extracted into a fresh directory. The second
fixture render used that extracted source, not the working source folder.
Results: **22 pages, 528 local references, 44 integrity references, six search
records, and 37 Chromium assertions passed**. No local URL escaped the project
prefix. The candidate ZIP's CRC check also passed.

The final ZIP has the same tested website code, with this report, screenshots,
and recorded test results added. A final byte-for-byte manifest check confirms
the delivered website source matches the tested candidate.

## Browser checks actually executed

The browser loaded local fixture HTML directly, with CSS, JS, and illustrations
inlined. The JSON search response and optional localStorage interface were
mocked because there was no accessible HTTP origin. The actual site's search
ranking, DOM rendering, theme, motion, filtering, and menu handlers ran as
written. Clipboard controls were tested for honest success/failure feedback,
not cross-browser permission behavior.

The checks included:

- Custom homepage rather than a rendered README.
- Dark/light toggling and interactive stack-layer selection.
- Decorative animation pause/resume and reduced-motion preference.
- Search matches, no-results message, correct result URL prefix, slash shortcut,
  Escape closing, and focus restoration to the search opener.
- Topic filtering/reset and the dedicated search page.
- Article content, code-copy control, and reading progress.
- Mobile menu expansion and closing with Escape.
- Home layout at 360, 390, 768, 1024, and 1440 pixels.
- Journal, projects, about, archive, topics, search, 404, and article layouts at
  390 and 1440 pixels; no horizontal overflow or broken loaded images.
- Main content/navigation at 390 pixels with JavaScript disabled.
- No uncaught JavaScript exceptions in the tested fixtures.

The supplied test script also checks real theme persistence after reload in
normal HTTP mode; that extra assertion was intentionally not counted locally.
Screenshots were visually reviewed for desktop, mobile, and light mode.

## Bugs found and fixed during these checks

1. A decorative SVG layer could cover the system-layer selection controls.
   Decorative scene pointer events are now disabled, leaving buttons clickable.
2. Escape on a nonempty search input could clear the input without closing the
   dialog. An explicit Escape handler now closes it and restores focus.
3. Small-screen navigation needed a wrapping fallback when JavaScript is off.
   The no-JavaScript layout has that fallback.

## What GitHub Actions will do

The workflow `.github/workflows/pages.yml` is designed to:

1. Install official Hugo 0.166.0 with an SHA256-checked download.
2. Run source validation and JavaScript syntax checks.
3. Build with actual Hugo for `/`, run link/SRI/JSON/XML checks, and run normal
   HTTP Chromium tests against that generated output.
4. Independently build and test `/prashantdivate/` the same way.
5. Build again with the repository's real Pages URL and check that output.
6. Upload **only `public/`** and deploy it only after the build job succeeds.

The first successful GitHub workflow run is the remaining integration test.
See `DEPLOY.md`; do not treat the offline checks as a substitute for that run.

## Not covered

Live external links, search engine indexing, real social-card unfurls, DNS or
custom domains, Safari/Firefox, assistive-technology certification, audits of
technical claims in starter articles, GitHub service availability, and repository
or organization policies were not tested. This is a static website, with no
server-side login/form/database workflows to test.

## Recorded evidence

- `docs/verification-root.json` and `docs/verification-project.json`: per-check
  browser reports, explicitly marked `offline-fixture`.
- `docs/preview-desktop.png` and `docs/preview-mobile.png`: actual local browser
  captures of the rendered design, not images of a live GitHub deployment.
- `scripts/check_site.py`, `scripts/audit_source.py`, and
  `scripts/browser_test.py`: reusable verification scripts for actual builds.
