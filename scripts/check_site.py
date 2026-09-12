#!/usr/bin/env python3
"""Check generated Hugo output without third-party Python dependencies.

Usage: python scripts/check_site.py public --base-url https://user.github.io/
Checks all local href/src targets, fragments, SRI digests, search JSON and XML.
External URLs are intentionally not fetched. Python 3.11+ is recommended.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import posixpath
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.references: list[tuple[str, str, str | None]] = []
        self.duplicate_ids: list[str] = []
        self.titles = 0
        self.mains = 0
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        identifier = a.get('id')
        if identifier:
            if identifier in self.ids:
                self.duplicate_ids.append(identifier)
            self.ids.add(identifier)
        self.titles += tag == 'title'
        self.mains += tag == 'main'
        key = 'href' if tag in ('a', 'link') else 'src' if tag in ('img', 'script', 'source') else None
        if key and a.get(key):
            self.references.append((tag, a[key] or '', a.get('integrity')))


def verify(root: Path, base_url: str) -> dict[str, int]:
    root = root.resolve()
    base_url = base_url.rstrip('/') + '/'
    base = urlsplit(base_url)
    errors: list[str] = []
    documents: dict[Path, PageParser] = {}
    html_files = sorted(root.rglob('*.html'))
    if not html_files or not (root / 'index.html').is_file():
        raise ValueError(f'{root} does not contain a generated index.html')
    for file in html_files:
        parser = PageParser()
        source = file.read_text(encoding='utf-8')
        parser.feed(source)
        documents[file] = parser
        if 'ZgotmplZ' in source:
            errors.append(f'{file.relative_to(root)}: unsafe or invalid template URL')
        if parser.duplicate_ids:
            errors.append(f'{file.relative_to(root)}: duplicate IDs: {parser.duplicate_ids}')
        # The accessible inline SVG also has a title; at least one title is needed.
        if not parser.titles or parser.mains != 1:
            errors.append(f'{file.relative_to(root)}: expected a title and exactly one main element')
    references = 0
    integrity_checks = 0
    def local_target(address: str, current: Path) -> tuple[Path, str] | None:
        if address.startswith(('data:', 'mailto:', 'tel:', 'javascript:')):
            return None
        current_url = urljoin(base_url, current.relative_to(root).as_posix())
        resolved = urlsplit(urljoin(current_url, address))
        if resolved.scheme not in ('http', 'https') or resolved.netloc != base.netloc:
            return None
        path = unquote(resolved.path)
        if not path.startswith(base.path):
            errors.append(f'{current.relative_to(root)}: URL escapes site prefix: {address}')
            return None
        local = path[len(base.path):]
        target = (root / posixpath.normpath(local)).resolve()
        if not target.is_relative_to(root):
            errors.append(f'{current.relative_to(root)}: invalid local path: {address}')
            return None
        if target.is_dir():
            target /= 'index.html'
        return target, unquote(resolved.fragment)
    for file, parser in documents.items():
        for tag, address, integrity in parser.references:
            target_info = local_target(address, file)
            if target_info is None:
                continue
            references += 1
            target, fragment = target_info
            if not target.is_file():
                errors.append(f'{file.relative_to(root)}: missing {tag} target: {address}')
                continue
            if fragment and target.suffix == '.html':
                target_doc = documents.get(target)
                if target_doc is not None and fragment not in target_doc.ids:
                    errors.append(f'{file.relative_to(root)}: missing fragment: {address}')
            if integrity:
                algorithm, expected = integrity.split('-', 1)
                if algorithm not in ('sha256', 'sha384', 'sha512'):
                    errors.append(f'Unsupported integrity algorithm: {algorithm}')
                else:
                    actual = base64.b64encode(hashlib.new(algorithm, target.read_bytes()).digest()).decode()
                    if actual != expected:
                        errors.append(f'{target.relative_to(root)}: integrity mismatch')
                    integrity_checks += 1
    index_path = root / 'index.json'
    try:
        index = json.loads(index_path.read_text(encoding='utf-8'))
        if not isinstance(index, list):
            raise ValueError('search index is not a list')
        for entry in index:
            if not isinstance(entry.get('title'), str) or not isinstance(entry.get('url'), str):
                raise ValueError('search entry lacks a title or URL')
            target = local_target(entry['url'], root / 'index.html')
            if not target or not target[0].is_file():
                errors.append(f'Search entry does not resolve: {entry.get("url")}')
    except (OSError, ValueError, TypeError) as exc:
        errors.append(f'Invalid search index: {exc}')
        index = []
    for required in ('404.html', 'index.xml', 'sitemap.xml', 'robots.txt', 'favicon.svg', 'images/social-card.png'):
        if not (root / required).is_file():
            errors.append(f'Missing generated file: {required}')
    for xml in root.rglob('*.xml'):
        try:
            ET.parse(xml)
        except ET.ParseError as exc:
            errors.append(f'{xml.relative_to(root)}: invalid XML: {exc}')
    home = (root / 'index.html').read_text(encoding='utf-8')
    if 'site-header' not in home or 'hero-copy' not in home:
        errors.append('Homepage is not the custom website; refusing a README-only deployment.')
    if errors:
        raise ValueError('\n'.join(errors))
    return {'html_pages': len(html_files), 'local_references': references,
            'integrity_checks': integrity_checks, 'search_entries': len(index)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    parser.add_argument('--base-url', required=True)
    args = parser.parse_args()
    try:
        result = verify(args.site, args.base_url)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'SITE CHECK FAILED\n{exc}\n')
    print('SITE CHECK PASSED ' + json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    main()
