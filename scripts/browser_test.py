#!/usr/bin/env python3
"""Browser smoke/regression tests for generated Hugo output.

CI: python scripts/browser_test.py public --base-url http://127.0.0.1:8765/
Dependencies: pip install -r scripts/requirements-test.txt
              python -m playwright install chromium
A local HTTP server is started and stopped automatically. No live deployment
or external service is touched. Assertions adapt to the published post count.
"""
from __future__ import annotations
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from pathlib import Path
import threading
from urllib.parse import urljoin, urlsplit
from playwright.sync_api import sync_playwright, expect


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class Suite:
    def __init__(self, page, site: Path, base_url: str, output: Path, report: dict, loader=None):
        self.page = page
        self.site = site
        self.base_url = base_url.rstrip('/') + '/'
        self.output = output
        self.report = report
        self.loader = loader
        self.entries = json.loads((site / 'index.json').read_text(encoding='utf-8'))
        self.errors: list[str] = []
        page.on('pageerror', lambda error: self.errors.append(str(error)))
        page.set_default_timeout(7000)

    def mark(self, text: str):
        self.report['passed'].append(text)

    def load(self, route: str = ''):
        if self.loader:
            self.loader(self.page, route)
        else:
            response = self.page.goto(urljoin(self.base_url, route), wait_until='networkidle')
            assert response and response.status == 200, f'Navigation failed: {route}'
        expect(self.page.locator('main')).to_have_count(1)
        self.page.evaluate('window.scrollTo(0, 0)')

    def overflow_check(self, label: str):
        size = self.page.evaluate('({w:innerWidth, s:document.documentElement.scrollWidth})')
        assert size['s'] <= size['w'] + 1, f'Horizontal overflow on {label}: {size}'
        broken = self.page.locator('img').evaluate_all('(images) => images.filter(i => i.complete && !i.naturalWidth).length')
        assert broken == 0, f'Broken images on {label}'
        self.mark(f'Layout fits viewport and images resolve: {label}')

    def interactions(self):
        p = self.page
        self.load()
        expect(p.locator('.hero-copy h1')).to_be_visible()
        self.mark('Custom homepage, not README')
        p.locator('.theme-toggle').click()
        expect(p.locator('html')).to_have_attribute('data-theme', 'light')
        if not self.loader:
            p.reload(wait_until='networkidle')
            expect(p.locator('html')).to_have_attribute('data-theme', 'light')
            self.mark('Theme preference persists after a real reload')
        p.wait_for_timeout(300)
        p.screenshot(path=str(self.output / 'desktop-light.png'))
        p.locator('.theme-toggle').click()
        expect(p.locator('html')).to_have_attribute('data-theme', 'dark')
        self.mark('Dark and light theme toggle')
        expect(p.locator('.workbench-scene')).to_be_visible()
        expect(p.locator('.workbench-svg')).to_have_count(1)
        expect(p.locator('.stack-caption')).to_contain_text('Yocto images')
        self.mark('Homepage technical workbench illustration')
        p.locator('.motion-toggle').click()
        expect(p.locator('html')).to_have_attribute('data-motion', 'off')
        p.locator('.motion-toggle').click()
        expect(p.locator('html')).to_have_attribute('data-motion', 'on')
        self.mark('Decorative animation pause and resume')
        p.evaluate('window.scrollTo(0, 0)')
        p.keyboard.press('/')
        expect(p.locator('#search-dialog')).to_be_visible()
        expect(p.locator('#dialog-search-input')).to_be_focused()
        if self.entries:
            p.locator('#dialog-search-input').fill(self.entries[0]['title'])
            expect(p.locator('#search-dialog .search-result').first).to_be_visible()
            expect(p.locator('#search-dialog .search-result').first).to_contain_text(self.entries[0]['title'])
            href = p.locator('#search-dialog .search-result').first.get_attribute('href')
            assert href and urlsplit(href).path.startswith(urlsplit(self.base_url).path)
            self.mark('Search finds article and retains correct site prefix')
        p.locator('#dialog-search-input').fill('qxz_no_possible_result_49384')
        expect(p.locator('#search-dialog .search-status')).to_contain_text('No results')
        p.keyboard.press('Escape')
        expect(p.locator('#search-dialog')).not_to_be_visible()
        self.mark('Search no-results state, keyboard opening and Escape closing')
        p.locator('[data-open-search]').click()
        p.locator('[data-close-search]').click()
        expect(p.locator('[data-open-search]')).to_be_focused()
        self.mark('Search restores keyboard focus to opener')
        self.load('posts/')
        cards = p.locator('[data-post-tags]')
        assert cards.count() == len(self.entries)
        choices = p.locator('[data-filter]:not([data-filter="all"])')
        if choices.count():
            selected = choices.first.get_attribute('data-filter')
            expected = cards.evaluate_all('(cards, tag) => cards.filter(c => c.dataset.postTags.split("|").includes(tag)).length', selected)
            choices.first.click()
            expect(p.locator('[data-post-tags]:visible')).to_have_count(expected)
            p.locator('[data-filter="all"]').click()
            expect(p.locator('[data-post-tags]:visible')).to_have_count(len(self.entries))
            self.mark('Topic filtering and reset against all published posts')
        self.load('search/')
        expect(p.locator('.search-page .search-status')).to_contain_text('Recent fieldnotes')
        self.mark('Dedicated searchable article index')
        if self.entries:
            first_path = urlsplit(self.entries[0]['url']).path
            prefix = urlsplit(self.base_url).path
            route = first_path[len(prefix):]
            self.load(route)
            expect(p.locator('#article-content')).to_be_visible()
            if p.locator('.prose pre code').count():
                copy = p.locator('.copy-code').first
                expect(copy).to_be_visible()
                copy.click()
                expect(copy).to_have_text(re.compile('Copied|Select to copy'))
                self.mark('Code-copy control reports success or unavailable permission')
            p.evaluate('document.querySelector(".article-end").scrollIntoView()')
            p.wait_for_timeout(150)
            transform = p.locator('.reading-progress > span').evaluate('(e) => getComputedStyle(e).transform')
            assert transform != 'matrix(0, 0, 0, 1, 0, 0)', 'Article reading progress remained at zero'
            self.mark('Article content, table-of-contents targets and reading progress')
            p.evaluate('window.scrollTo(0, 0)')
            p.screenshot(path=str(self.output / 'article-desktop.png'), full_page=True)
        p.set_viewport_size({'width': 390, 'height': 844})
        self.load()
        menu = p.locator('.menu-toggle')
        menu.click()
        expect(menu).to_have_attribute('aria-expanded', 'true')
        expect(p.locator('#site-nav')).to_be_visible()
        p.keyboard.press('Escape')
        expect(menu).to_have_attribute('aria-expanded', 'false')
        self.mark('Mobile navigation expands and closes with Escape')
        p.emulate_media(reduced_motion='reduce')
        expect(p.locator('html')).to_have_attribute('data-motion', 'off')
        expect(p.locator('.motion-toggle')).to_be_disabled()
        self.mark('System reduced-motion preference disables decorative animations')
        p.emulate_media(reduced_motion='no-preference')

    def layouts(self):
        p = self.page
        for width in (360, 390, 768, 1024, 1440):
            p.set_viewport_size({'width': width, 'height': 900})
            self.load()
            self.overflow_check(f'homepage {width}px')
            if width == 1440:
                p.screenshot(path=str(self.output / 'desktop-home.png'))
                p.screenshot(path=str(self.output / 'desktop-home-full.png'), full_page=True)
            if width == 390:
                p.screenshot(path=str(self.output / 'mobile-home.png'), full_page=True)
        routes = ['posts/', 'projects/', 'about/', 'archive/', 'tags/', 'search/', '404.html']
        if self.entries:
            first = urlsplit(self.entries[0]['url']).path
            routes.append(first[len(urlsplit(self.base_url).path):])
        for width in (390, 1440):
            p.set_viewport_size({'width': width, 'height': 900})
            for route in routes:
                self.load(route)
                self.overflow_check(f'{route} {width}px')
        assert not self.errors, '\n'.join(self.errors)
        self.mark('No uncaught JavaScript exceptions in tested pages')


def run_suite(site: Path, base_url: str, output: Path, executable: str | None = None, loader=None):
    output.mkdir(parents=True, exist_ok=True)
    report = {'mode': 'offline-fixture' if loader else 'HTTP generated-site', 'passed': [], 'failed': None}
    with sync_playwright() as manager:
        options = {'headless': True}
        if executable:
            options['executable_path'] = executable
        browser = manager.chromium.launch(**options)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='no-preference')
        page = context.new_page()
        try:
            suite = Suite(page, site, base_url, output, report, loader)
            suite.interactions()
            suite.layouts()
            # Navigation and article content must remain usable without JavaScript.
            plain = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
            plain_page = plain.new_page()
            plain_suite = Suite(plain_page, site, base_url, output, report, loader)
            plain_suite.load()
            expect(plain_page.locator('#site-nav a').first).to_be_visible()
            expect(plain_page.locator('.hero-copy h1')).to_be_visible()
            plain_suite.overflow_check('homepage 390px, JavaScript disabled')
            report['passed'].append('Primary navigation and content usable without JavaScript')
            plain.close()
        except Exception as exc:
            report['failed'] = str(exc)
            try:
                page.screenshot(path=str(output / 'failure.png'), full_page=True)
            except Exception:
                pass
            raise
        finally:
            report['pass_count'] = len(report['passed'])
            (output / 'browser-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            browser.close()
    print(f'BROWSER CHECKS PASSED: {len(report["passed"])}; mode={report["mode"]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    parser.add_argument('--base-url', default='http://127.0.0.1:8765/')
    parser.add_argument('--output', type=Path, default=Path('test-results'))
    parser.add_argument('--chromium', help='Optional existing Chromium executable')
    args = parser.parse_args()
    site = args.site.resolve()
    url = urlsplit(args.base_url)
    if url.scheme != 'http' or url.hostname not in ('127.0.0.1', 'localhost'):
        parser.error('Browser tests must target a local http://127.0.0.1 or localhost URL.')
    # Serve the parent directory for a site built beneath a project prefix.
    server_root = site
    for component in reversed([part for part in url.path.split('/') if part]):
        if server_root.name != component:
            parser.error('Site directory names must match the project path in --base-url.')
        server_root = server_root.parent
    server = ThreadingHTTPServer((url.hostname, url.port or 8765), partial(QuietHandler, directory=str(server_root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        run_suite(site, args.base_url, args.output, args.chromium)
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
