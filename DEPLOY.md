# First deployment - use this one path

Target repository: **prashantdivate.github.io**
Target site: **https://prashantdivate.github.io/**

You do not need to install Hugo or run npm locally for this deployment.
GitHub Actions installs the pinned Hugo release and builds the site.

## 1. Back up your current site

Keep a copy of the old source outside the repository before replacing anything.
Do not mix this project with the earlier Hugo, Jekyll, or static-HTML packages.
No force push, history reset, or Git repository deletion is needed.

## 2. Clone the repository

Run this from a parent working folder in Git Bash, PowerShell, or a terminal:

```bash
git clone https://github.com/prashantdivate/prashantdivate.github.io.git
cd prashantdivate.github.io
```

If you already have a clean local clone, use it instead. `git status` should
show no unrelated uncommitted work. Back up/commit that work first.

If the repository does not exist yet, create it on GitHub with the exact name
above, visibility **Public**, and an initial README. Then clone it. The next
steps replace that README with this project's README and source.

## 3. Replace the old website source

Extract the ZIP outside your repository. Inside it is `prashant-edge-systems-lab/`.

In the cloned repository, remove the old website files and the old `.github`
folder **after backing them up**. **Keep `.git/` intact.** Keep any unrelated
files you deliberately need. If you use a custom domain, see the note below
before deleting an existing CNAME.

Copy **everything inside `prashant-edge-systems-lab/`** into the cloned repository,
including the hidden `.github`, `.hugo-version`, and `.gitignore` files.
Do not copy the outer folder as a nested folder.

The result must be:

```text
prashantdivate.github.io/
|-- .git/                         existing Git history - preserve it
|-- .github/workflows/pages.yml   the only site deployment workflow
|-- .hugo-version
|-- hugo.toml
|-- README.md
|-- DEPLOY.md
|-- content/
|-- data/
|-- layouts/
|-- assets/
|-- static/
|-- archetypes/
`-- scripts/
```

It is correct that there is **no source-root `index.html`**. Hugo generates it
in `public/`. That generated directory is what the workflow publishes.

## 4. Configure Pages BEFORE pushing

In GitHub, open:

**Repository > Settings > Pages > Build and deployment > Source**

Select **GitHub Actions**.

Do not select "Deploy from a branch", `main / (root)`, or `/docs`.
You do not need to click GitHub's suggested Jekyll workflow setup button; the
correct workflow is already in this package.

Also ensure repository Actions are enabled. Organization policy can restrict
which actions run; that policy must permit the included GitHub actions.

## 5. Commit and push

From the cloned repository:

```bash
git status
git add -A
git commit -m "Launch Edge Systems Lab Hugo portfolio and blog"
git push
```

The workflow accepts `main` or `master` when it is the repository's default
branch. Do not rename branches merely to publish this project. Other branch
names need a corresponding edit to the workflow's `on.push.branches` list.

If you enabled Pages only after the push, open **Actions > Build, verify and
deploy Edge Systems Lab > Run workflow**, select the default branch, and run it.

## 6. Watch the actual verification and deployment

Open the latest run under **Actions**. It should show:

```text
build
  source validation
  install pinned Hugo and test browser
  verification pass 1: root URL build + checks
  verification pass 2: project URL build + checks
  production build using the real Pages URL
  upload generated public/ artifact

deploy
  publish artifact to GitHub Pages
```

Both jobs must be green. If `build` fails, `deploy` is skipped. Do not change to
branch publishing to work around a failed Hugo build; read the failed step.
Browser reports/screenshots are attached to the run when available.

## 7. Open your website

Use the link from the green `deploy` job or **Settings > Pages > Visit site**.
For the recommended repository the address is:

**https://prashantdivate.github.io/**

Check the homepage, Journal, Projects, About, a post, search, and mobile menu.
Use a hard refresh if an old page remains cached. Deployment is not confirmed
until GitHub's jobs succeed and the actual site loads correctly.

## What about another repository name?

The recommended instructions above deliberately use one repository name. The
workflow obtains the production URL from `actions/configure-pages`, so it also
supports a project repository such as `prashantdivate`, without hard-coding a
`/prashantdivate/` prefix into assets. The ordinary URL would then include that
repository name. GitHub's own deployment URL is the authoritative address.

The `hugo.toml` base URL is the default for local/manual builds. GitHub Actions
overrides it with the actual configured Pages URL during production builds.

## Troubleshooting

| Symptom | Check |
|---|---|
| README is displayed again | Pages Source must be **GitHub Actions**, and `deploy` must have completed. |
| No workflow appears | `.github/workflows/pages.yml` must be in the repository root, not inside a wrapper folder. |
| Workflow does not run after push | Push the default `main` or `master` branch; confirm Actions are enabled. |
| Pages configuration step fails | Enable Pages/Actions first; rerun. Check repository/organization permissions. |
| Source audit detects extra workflows | Remove the old site's Hugo/Jekyll deployment workflow; keep this `pages.yml`. |
| Hugo or browser test fails | Open the failed step and its artifact. Do not publish source instead of generated output. |
| Article is missing | Check `draft`, publication date/time, valid TOML, and its `content/posts/` location. |
| Old design still appears | Confirm the latest deployment is green, open its URL, then hard-refresh. |
| Push is rejected | Pull/reconcile the remote changes. Do not force-push over work you have not reviewed. |

## Custom domain note

No custom domain is configured in this package. If you already own and use one,
preserve its Pages settings and move the existing CNAME value to `static/CNAME`
so Hugo includes it in the generated site. Review domain and DNS settings
separately; these are not tested by this project.

## Official references

- Hugo Pages guide: https://gohugo.io/host-and-deploy/host-on-github-pages/
- GitHub custom workflows: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- Torizon's Hugo deployment: https://github.com/torizon/blog/blob/main/.github/workflows/hugo.yaml
