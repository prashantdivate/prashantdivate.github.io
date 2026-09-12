#!/usr/bin/env python3
"""Audit content, configuration, and required files. Does not replace a Hugo build."""
from __future__ import annotations
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    errors: list[str] = []
    required = ['hugo.toml', '.hugo-version', '.github/workflows/pages.yml',
                'layouts/baseof.html', 'layouts/home.html', 'layouts/home.json.json',
                'layouts/posts/page.html', 'layouts/posts/section.html',
                'layouts/_partials/head.html', 'assets/css/main.css', 'assets/js/main.js',
                'static/favicon.svg', 'static/images/social-card.png']
    for name in required:
        if not (ROOT / name).is_file():
            errors.append(f'Missing {name}')
    config = tomllib.loads((ROOT / 'hugo.toml').read_text(encoding='utf-8'))
    if config.get('buildDrafts') or config.get('buildFuture'):
        errors.append('Production must not automatically publish drafts or future posts.')
    for name in ('profile', 'projects'):
        json.loads((ROOT / f'data/{name}.json').read_text(encoding='utf-8'))
    posts = 0
    for file in (ROOT / 'content').rglob('*.md'):
        text = file.read_text(encoding='utf-8')
        try:
            if not text.startswith('+++\n'):
                raise ValueError('Use TOML front matter between +++ lines.')
            metadata = tomllib.loads(text.split('+++', 2)[1])
            if not metadata.get('title'):
                raise ValueError('title is required')
            if 'posts' in file.relative_to(ROOT / 'content').parts and file.name != '_index.md':
                posts += 1
                for key in ('date', 'description', 'draft'):
                    if key not in metadata:
                        raise ValueError(f'{key} is required')
                if not isinstance(metadata.get('tags', []), list):
                    raise ValueError('tags must be a list')
                art = metadata.get('art', config['params']['defaultArt'])
                if not (ROOT / f'static/images/art-{art}.svg').is_file():
                    raise ValueError(f'Missing illustration for art = {art!r}')
        except (ValueError, IndexError, tomllib.TOMLDecodeError) as exc:
            errors.append(f'{file.relative_to(ROOT)}: {exc}')
    workflows = list((ROOT / '.github/workflows').glob('*.y*ml'))
    if len(workflows) != 1:
        errors.append('Keep only the included Pages workflow. Remove obsolete Hugo/Jekyll workflows.')
    if errors:
        sys.exit('SOURCE AUDIT FAILED\n' + '\n'.join(errors))
    print(f'SOURCE AUDIT PASSED: {posts} post files; configuration and content parsed.')

if __name__ == '__main__':
    main()
