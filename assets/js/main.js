(() => {
  const q = (s, c=document) => c.querySelector(s);
  const qa = (s, c=document) => [...c.querySelectorAll(s)];

  const toggle = q('#menuToggle');
  const mobile = q('#mobileNav');
  if (toggle && mobile) toggle.addEventListener('click', () => mobile.classList.toggle('open'));

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('visible'); observer.unobserve(entry.target); } });
  }, { threshold: .08 });
  qa('.reveal').forEach(el => observer.observe(el));

  const topBtn = q('#toTop');
  if (topBtn) {
    window.addEventListener('scroll', () => topBtn.classList.toggle('show', scrollY > 500), {passive:true});
    topBtn.addEventListener('click', () => scrollTo({top:0, behavior:'smooth'}));
  }

  const filters = qa('.filter');
  const rows = qa('.post-row');
  filters.forEach(btn => btn.addEventListener('click', () => {
    filters.forEach(x => x.classList.remove('active')); btn.classList.add('active');
    const f = btn.dataset.filter;
    rows.forEach(row => row.style.display = f === 'all' || (row.dataset.tags || '').split(' ').includes(f) ? '' : 'none');
  }));

  const searchInput = q('#searchInput');
  const resultBox = q('#searchResults');
  const meta = q('#searchMeta');
  let index = [];
  if (searchInput && resultBox && window.SEARCH_INDEX_URL) {
    fetch(window.SEARCH_INDEX_URL).then(r => r.json()).then(data => index = data).catch(() => { if(meta) meta.textContent = 'Search index unavailable.'; });
    const render = () => {
      const term = searchInput.value.trim().toLowerCase();
      if (!term) { resultBox.innerHTML=''; meta.textContent='Start typing to search.'; return; }
      const terms = term.split(/\s+/).filter(Boolean);
      const hits = index.filter(item => terms.every(t => [item.title,item.description,(item.tags||[]).join(' '),item.content].join(' ').toLowerCase().includes(t))).slice(0,20);
      meta.textContent = `${hits.length} result${hits.length===1?'':'s'} for “${searchInput.value}”`;
      resultBox.innerHTML = hits.map(hit => `<a class="search-hit" href="${hit.url}"><div class="post-topline"><span>${(hit.tags||['Engineering'])[0]}</span><time>${hit.date}</time></div><h3>${escapeHtml(hit.title)}</h3><p>${escapeHtml(hit.description||'')}</p></a>`).join('');
    };
    searchInput.addEventListener('input', render);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') { searchInput.value=''; render(); searchInput.blur(); } if (e.key==='/' && document.activeElement !== searchInput) { e.preventDefault(); searchInput.focus(); } });
  }
  function escapeHtml(s=''){ return s.replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
})();
