/* Fieldnotes: progressively enhanced, dependency-free interactions.
   Content, navigation, articles, and project links work without this script. */
(() => {
  'use strict';
  const root = document.documentElement;
  root.classList.add('js');
  const one = (selector, parent = document) => parent.querySelector(selector);
  const all = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const storage = {
    get(key) { try { return localStorage.getItem(key); } catch (_) { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch (_) { /* Preferences are optional. */ } }
  };

  // Preferences: no cookies, analytics, network calls, or external scripts.
  const themeButton = one('.theme-toggle');
  function refreshTheme() {
    const light = root.dataset.theme === 'light';
    if (themeButton) themeButton.setAttribute('aria-label', `Switch to ${light ? 'dark' : 'light'} theme`);
    const meta = one('meta[name="theme-color"]');
    if (meta) meta.content = light ? '#f6f7f0' : '#101310';
  }
  if (themeButton) themeButton.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
    storage.set('fieldnotes-theme', root.dataset.theme);
    refreshTheme();
  });
  refreshTheme();

  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const motionButton = one('.motion-toggle');
  function refreshMotion() {
    const off = reducedMotion.matches || storage.get('fieldnotes-motion') === 'off';
    root.dataset.motion = off ? 'off' : 'on';
    if (!motionButton) return;
    one('[data-motion-label]', motionButton).textContent = off ? 'off' : 'on';
    motionButton.setAttribute('aria-pressed', String(!off));
    motionButton.disabled = reducedMotion.matches;
    motionButton.title = reducedMotion.matches ? 'Reduced motion is enabled in your system settings.' : 'Pause or resume decorative animations';
  }
  if (motionButton) motionButton.addEventListener('click', () => {
    storage.set('fieldnotes-motion', root.dataset.motion === 'on' ? 'off' : 'on');
    refreshMotion();
  });
  reducedMotion.addEventListener('change', refreshMotion);
  refreshMotion();

  // Mobile navigation. Escape and navigation both close the menu.
  const menuButton = one('.menu-toggle');
  const navigation = one('#site-nav');
  function closeMenu() {
    if (!navigation || !menuButton) return;
    navigation.classList.remove('is-open');
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'Open navigation');
  }
  if (menuButton && navigation) {
    menuButton.addEventListener('click', () => {
      const open = navigation.classList.toggle('is-open');
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', `${open ? 'Close' : 'Open'} navigation`);
    });
    all('a', navigation).forEach(link => link.addEventListener('click', closeMenu));
    document.addEventListener('click', event => {
      if (!navigation.contains(event.target) && !menuButton.contains(event.target)) closeMenu();
    });
    matchMedia('(min-width: 681px)').addEventListener('change', closeMenu);
  }

  // A one-time entrance animation. Elements are never hidden by default.
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('was-revealed');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08 });
    all('[data-reveal]').forEach(element => observer.observe(element));
  }

  // Blog filtering only affects this page; it never filters a partial pager.
  all('[data-filterable]').forEach(section => {
    const cards = all('[data-post-tags]', section);
    const buttons = all('[data-filter]', section);
    buttons.forEach(button => button.addEventListener('click', () => {
      const selected = button.dataset.filter;
      let visible = 0;
      cards.forEach(card => {
        const tags = card.dataset.postTags.split('|');
        const show = selected === 'all' || tags.includes(selected);
        card.hidden = !show;
        if (show) visible += 1;
      });
      buttons.forEach(other => {
        other.classList.toggle('is-active', other === button);
        other.setAttribute('aria-pressed', String(other === button));
      });
      const status = one('.filter-status', section);
      if (status) status.textContent = `${visible} ${visible === 1 ? 'note' : 'notes'} shown.`;
      const empty = one('.no-posts', section);
      if (empty) empty.hidden = visible !== 0;
    }));
  });

  // Load the static Hugo-generated search index once, when it is needed.
  const indexPromises = new Map();
  function loadIndex(url) {
    if (!indexPromises.has(url)) {
      const request = fetch(url, { credentials: 'same-origin' }).then(response => {
        if (!response.ok) throw new Error(`Search index returned HTTP ${response.status}`);
        return response.json();
      }).then(items => {
        if (!Array.isArray(items)) throw new Error('Invalid search index');
        return items.filter(item => item && typeof item.title === 'string' && typeof item.url === 'string');
      }).catch(error => {
        indexPromises.delete(url); // A later query can retry a transient failure.
        throw error;
      });
      indexPromises.set(url, request);
    }
    return indexPromises.get(url);
  }
  function safeLocalURL(path) {
    try {
      const url = new URL(path, document.baseURI);
      return url.origin === new URL(document.baseURI).origin && ['http:', 'https:'].includes(url.protocol) ? url.href : null;
    } catch (_) { return null; }
  }
  function renderResults(container, items) {
    container.replaceChildren();
    items.forEach(item => {
      const url = safeLocalURL(item.url);
      if (!url) return;
      const link = document.createElement('a');
      link.className = 'search-result';
      link.href = url;
      const title = document.createElement('strong');
      title.textContent = item.title;
      const description = document.createElement('p');
      description.textContent = item.description || '';
      const tags = document.createElement('small');
      tags.textContent = (Array.isArray(item.tags) ? item.tags : []).join(' / ');
      link.append(title, description, tags);
      container.append(link);
    });
  }
  all('[data-search]').forEach(search => {
    const input = one('input', search);
    const status = one('.search-status', search);
    const results = one('.search-results', search);
    let timer;
    let generation = 0;
    async function runSearch() {
      const current = ++generation;
      const query = input.value.trim().toLocaleLowerCase();
      status.textContent = 'Searching the blogs...';
      try {
        const items = await loadIndex(search.dataset.index);
        if (current !== generation) return;
        const words = query.split(/\s+/).filter(Boolean);
        const matches = items.map(item => {
          const title = item.title.toLocaleLowerCase();
          const tags = (item.tags || []).join(' ').toLocaleLowerCase();
          const full = `${title} ${tags} ${item.description || ''} ${item.content || ''}`.toLocaleLowerCase();
          const match = words.every(word => full.includes(word));
          const score = words.reduce((total, word) => total + (title.includes(word) ? 6 : 0) + (tags.includes(word) ? 3 : 0), 0);
          return { item, match, score };
        }).filter(result => result.match).sort((a, b) => b.score - a.score || String(b.item.date).localeCompare(String(a.item.date)));
        renderResults(results, matches.slice(0, 20).map(result => result.item));
        status.textContent = query
          ? (matches.length ? `${matches.length} ${matches.length === 1 ? 'result' : 'results'}${matches.length > 20 ? ' (showing the first 20)' : ''}.` : 'No results. Try a different term, or browse the archive.')
          : 'Recent fieldnotes. Start typing to narrow the list.';
      } catch (_) {
        if (current !== generation) return;
        results.replaceChildren();
        status.textContent = 'Search could not load. Try again, or browse Blogs or Archive.';
      }
    }
    input.addEventListener('input', () => {
      ++generation;
      clearTimeout(timer);
      timer = setTimeout(runSearch, 100);
    });
    input.addEventListener('focus', () => { if (!results.children.length) runSearch(); });
    if (search.closest('.search-page')) runSearch();
  });

  const dialog = one('#search-dialog');
  let opener;
  function openSearch(event) {
    if (!dialog || typeof dialog.showModal !== 'function') return;
    if (event) event.preventDefault();
    if (dialog.open) return;
    closeMenu();
    opener = document.activeElement;
    dialog.showModal();
    one('input', dialog).focus();
  }
  all('[data-open-search]').forEach(trigger => trigger.addEventListener('click', openSearch));
  if (dialog) {
    const close = one('[data-close-search]', dialog);
    if (close) close.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      const box = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
    });
    dialog.addEventListener('close', () => { if (opener && opener.isConnected) opener.focus(); });
  }
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      closeMenu();
      // Search inputs may otherwise consume Escape just to clear their value.
      if (dialog && dialog.open) { event.preventDefault(); dialog.close(); }
      return;
    }
    const typing = event.target instanceof Element && (event.target.matches('input, textarea, select') || event.target.isContentEditable);
    if (!typing && ((event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey) || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k'))) openSearch(event);
  });

  // Copy helpers report failure honestly when browser permissions block them.
  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const field = document.createElement('textarea');
    field.value = text;
    field.style.cssText = 'position:fixed;left:-9999px;top:0';
    document.body.append(field);
    field.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } finally { field.remove(); }
    if (!copied) throw new Error('Clipboard permission not available');
  }
  function copyFeedback(button, text, original) {
    button.textContent = text;
    button.setAttribute('aria-label', text);
    setTimeout(() => { button.innerHTML = original; button.removeAttribute('aria-label'); }, 1800);
  }
  all('.prose pre').forEach(pre => {
    const code = one('code', pre);
    if (!code) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = 'Copy';
    button.addEventListener('click', async () => {
      try { await copyText(code.textContent); copyFeedback(button, 'Copied', 'Copy'); }
      catch (_) { copyFeedback(button, 'Select to copy', 'Copy'); }
    });
    pre.append(button);
  });
  const pageCopy = one('.copy-page');
  if (pageCopy) pageCopy.addEventListener('click', async () => {
    const original = pageCopy.innerHTML;
    try { await copyText(location.href); copyFeedback(pageCopy, 'Link copied', original); }
    catch (_) { copyFeedback(pageCopy, 'Copy the address bar', original); }
  });

  // Article progress is tied to the article, not the footer or related cards.
  const article = one('#article-content');
  const progress = one('.reading-progress > span');
  if (article && progress) {
    const headings = all('h2[id], h3[id]', article);
    const links = all('#TableOfContents a');
    let scheduled = false;
    function updateArticle() {
      const top = article.getBoundingClientRect().top + window.scrollY;
      const bottom = top + article.offsetHeight;
      const denominator = Math.max(1, bottom - top - window.innerHeight + 130);
      const fraction = Math.max(0, Math.min(1, (window.scrollY - top + 130) / denominator));
      progress.style.transform = `scaleX(${fraction})`;
      let active = headings.length ? headings[0].id : '';
      headings.forEach(heading => { if (heading.getBoundingClientRect().top < 175) active = heading.id; });
      links.forEach(link => link.classList.toggle('is-active', decodeURIComponent(link.hash.slice(1)) === active));
      scheduled = false;
    }
    function scheduleUpdate() { if (!scheduled) { scheduled = true; requestAnimationFrame(updateArticle); } }
    window.addEventListener('scroll', scheduleUpdate, { passive: true });
    window.addEventListener('resize', scheduleUpdate);
    updateArticle();
  }
})();
