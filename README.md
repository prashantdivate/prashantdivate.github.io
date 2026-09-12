# Fieldnotes - Prashant Divate

An original, animated engineering portfolio and technical journal. **One stack:
Hugo + Markdown + a custom theme + GitHub Actions + GitHub Pages.**

The source belongs in the **root** of `prashantdivate.github.io`. It is not a
Jekyll project and not a folder of manually maintained article HTML.

> Read [DEPLOY.md](DEPLOY.md) for the exact first deployment steps.
> Read [VERIFICATION.md](VERIFICATION.md) for the checks actually run and their
> limitations. An actual Hugo build and live deployment were not executed in
> the package-creation environment. GitHub Actions runs the real build/tests.

## Included

- Responsive homepage, journal, project showcase, about page, archive, topics,
  individual articles, dedicated search page, and a custom 404 page.
- Animated layered-system illustration with interactive layer selection,
  subtle entrance/hover animations, and decorative orbit/trace effects.
- Dark and light modes, pause/resume motion, and system reduced-motion support.
- Static search with keyboard shortcut, topic filtering, article table of
  contents, reading progress, and code/link copying with error feedback.
- Six original **starter notes**, six original SVG covers, and concept visuals
  for Yocto-Lens and VulnTrack. No Torizon articles or branding are copied.
- RSS, sitemap, canonical/social metadata, and fingerprinted CSS/JavaScript.
- No website runtime packages, tracking, external fonts, database, or backend.
- One deployment workflow that tests root and project URLs, then uploads only
  Hugo's generated `public/` folder. The production URL comes from Pages.

## Fast path to publishing

1. Use the public repository **`prashantdivate.github.io`**.
2. Back up the old site. Replace its source with the **contents of this folder**,
   preserving the repository's `.git` directory. Remove the previous site's
   deployment workflows. Do not nest this folder or put it under `docs/`.
3. Set **Settings > Pages > Build and deployment > Source > GitHub Actions**.
4. Commit and push. Open **Actions > Build, verify and deploy Fieldnotes**.
5. Wait for both `build` and `deploy` to pass. Open the URL shown by deployment.

Do **not** select "Deploy from a branch". The repository contains Hugo source;
GitHub Actions must build it first. You do not need Hugo installed on your
computer just to commit and publish the source.

## Write a blog post

Create `content/posts/my-first-post/index.md`:

```toml
+++
title = 'My first fieldnote'
date = 2026-09-12T00:00:00+05:30
draft = false
description = 'A short summary of what the reader will learn.'
tags = ['Linux', 'Yocto']
art = 'linux'
sample = false
+++

Write your article in Markdown here.

## The problem

Explain the problem and its context.
```

Use a date at or before publication time. Future posts and `draft = true` posts
are not published. The newest published post automatically gets the large
homepage card; the next three get the smaller cards.

Available `art` values: `linux`, `ota`, `containers`, `build`, `security`, `notes`.
Add new covers as `static/images/art-NAME.svg` and use `art = 'NAME'`.
Put article-specific screenshots next to the post's `index.md`; use ordinary
Markdown such as `![Boot sequence](boot-sequence.png)`.

Commit and push: GitHub rebuilds the journal, topics, search index, and feed.
You can also create Markdown files through GitHub's **Add file** interface.

**Starter content:** the six supplied notes are examples, visibly marked
"Starter note". Review/replace them, delete unwanted ones, or set `draft = true`.
Only remove `sample = true` after reviewing a note. Do not present the examples
as documented production incidents or as writing you have not reviewed.

## Preview locally (optional)

Use Hugo **0.166.0**, as pinned in `.hugo-version`. Standard Hugo is sufficient;
Hugo Extended also works. There is no Sass or Node build to install.

Install the official release for your operating system:
https://github.com/gohugoio/hugo/releases/tag/v0.166.0

From this folder:

```bash
hugo version
hugo server -D
```

Open the address printed by Hugo, normally `http://localhost:1313/`.
`-D` is for local draft previews only. The deploy workflow does not publish drafts.
Do not open the template files directly in the browser.

Create a new draft using the included archetype:

```bash
hugo new content posts/my-first-post/index.md
```

## Maintenance map

| What to change | File or folder |
|---|---|
| Name, introduction, role, optional email/LinkedIn | `data/profile.json` |
| Project cards and repository links | `data/projects.json` |
| About-page text | `content/about.md` |
| Articles | `content/posts/<slug>/index.md` |
| Site title, defaults, local base URL | `hugo.toml` |
| Colors, typography, spacing, animations | `assets/css/main.css` |
| Theme/menu/search/filter interactions | `assets/js/main.js` |
| Shared header/footer/article/card markup | `layouts/` |
| New-post skeleton | `archetypes/default.md` |
| Original illustrations and social image | `static/images/` |
| Deployment and verification | `.github/workflows/pages.yml` |

Most updates need only Markdown or the two data files. There is no theme
submodule, npm dependency tree, or generated HTML to maintain. Templates use
Hugo's modern `layouts/home.html`, `page.html`, and `_partials/` organization.

## Tests

GitHub runs these automatically before each deployment:

```bash
python scripts/audit_source.py
node --check assets/js/main.js
hugo --gc --minify --baseURL 'http://127.0.0.1:8765/'
python scripts/check_site.py public --base-url 'http://127.0.0.1:8765/'
python -m pip install -r scripts/requirements-test.txt
python -m playwright install chromium
python scripts/browser_test.py public --base-url 'http://127.0.0.1:8765/'
```

Python 3.11+ is required for tests, not for the website. CI uses Python 3.12.
CI also repeats the actual Hugo build and browser checks under a project URL
prefix. Tests adapt to the published article count. A failed step blocks the
new deployment. Test reports/screenshots appear as an Actions artifact.

## Update dependencies deliberately

Hugo is pinned, not "latest". To upgrade it, change `.hugo-version`, update the
version guard and official SHA256 in `scripts/install-hugo.sh`, then review the
GitHub test results before deploying. Update GitHub Actions and the test-only
Playwright pin separately. The website itself has no third-party JS packages.

## Scope

This is a static portfolio/blog, not a CMS administration panel. There is no
login, comment database, newsletter backend, or contact-form submission service.
RSS and GitHub links are functional; no fake subscription forms are included.
Local storage is used only for optional theme and motion preferences.

See [ATTRIBUTION.md](ATTRIBUTION.md) for references and [LICENSE](LICENSE).
