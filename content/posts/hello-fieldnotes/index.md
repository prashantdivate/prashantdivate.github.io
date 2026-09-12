+++
title = "Hello, fieldnotes. A place for useful ideas."
date = 2026-09-01T09:00:00+05:30
draft = false
description = "A small, maintainable home for engineering notes. Write Markdown, push a commit, and let the publishing workflow do the rest."
tags = ["Tooling", "Writing"]
art = "notes"
sample = true
+++

This blog is a place for ideas that deserve more than a chat message and less than a textbook. The website is intentionally simple to maintain: content lives in Markdown files, layout lives in Hugo templates, and visual styling lives in one stylesheet.

This article is starter content. Replace it with your own introduction when you are ready.

## Write a new note

Create a page bundle with Hugo:

```bash
hugo new content posts/my-first-post/index.md
```

Edit the generated `index.md`. Give it a title, description, date, tags, and an illustration style. The included illustration keys are `linux`, `ota`, `containers`, `build`, `security`, and `notes`.

New pages are drafts by default, so unfinished work is not published by the production workflow.

## Preview before publishing

From the repository root:

```bash
hugo server -D
```

Open the local address Hugo prints. The `-D` option includes drafts in your local preview. It does not change the production build.

## Publish deliberately

When the article is ready, set `draft = false`, commit the change, and push it to the repository's default branch. GitHub Actions builds and checks the generated website before publishing the artifact.

```bash
git add content/posts/my-first-post/
git commit -m "Add my first fieldnote"
git push
```

You do not edit generated HTML or commit the `public` folder. The build creates that output again from your source files.

## Keep it personal

The profile text is in `data/profile.json`, and the project cards are in `data/projects.json`. These are the first files to customize after publishing.

The example articles are marked as starter notes. Replace them, or set their `draft` values to `true`. Do not publish private customer details, confidential company material, credentials, or logs containing secrets.

## References

- [Hugo content organization](https://gohugo.io/content-management/organization/)
- [Hugo on GitHub Pages](https://gohugo.io/host-and-deploy/host-on-github-pages/)
