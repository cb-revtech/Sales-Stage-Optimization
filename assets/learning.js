(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const items = [...document.querySelectorAll('.item')];
  const search = document.getElementById('search');
  const stage = document.getElementById('stage-filter');
  const count = document.getElementById('result-count');
  const empty = document.getElementById('empty');
  const label = document.body.dataset.page === 'definitions' ? 'definitions' : 'lessons';
  const letters = [...document.querySelectorAll('[data-letter]:not(.item)')];
  let letter = 'all';
  const normalize = s => s.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const text = new Map(items.map(item => [item, normalize((item.dataset.search || '') + ' ' + [...item.querySelectorAll('h2,h3,h4,p,li,summary')].map(node => node.textContent).join(' ')).split(/[^a-z0-9]+/).filter(Boolean)]));
  function filter() {
    const query = normalize(search.value.trim()).split(/[^a-z0-9]+/).filter(Boolean);
    let visible = 0;
    items.forEach(item => {
      const matches = query.every(word => text.get(item).some(token => word.length <= 3 ? token === word : token.startsWith(word))) &&
        (stage.value === 'all' || item.dataset.stages.split(' ').includes(stage.value)) &&
        (letter === 'all' || item.dataset.letter === letter);
      item.hidden = !matches;
      if (matches) visible++;
    });
    document.querySelectorAll('.deal-stream').forEach(stream => {
      const matches = [...stream.querySelectorAll('.item')].some(item => !item.hidden);
      stream.hidden = !matches;
      if (matches && (query.length || stage.value !== 'all')) stream.open = true;
    });
    count.textContent = `${visible} of ${items.length} ${label}`;
    empty.hidden = visible > 0;
    letters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.letter === letter)));
    document.querySelectorAll('.side [data-filter-stage]').forEach(link => {
      if (link.dataset.filterStage === stage.value) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
  }
  function reset() { search.value = ''; stage.value = 'all'; letter = 'all'; filter(); }
  function showHash() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    if (id.startsWith('filter-')) {
      const value = id.slice(7);
      if (![...stage.options].some(option => option.value === value)) return;
      reset(); stage.value = value; filter();
      document.getElementById('library').scrollIntoView({behavior:'instant',block:'start'});
      return;
    }
    const target = document.getElementById(id);
    if (!target) return;
    if (target.classList.contains('item') || target.closest('.item') || target.classList.contains('deal-stream')) {
      reset();
      let node = target;
      while (node && node !== document.body) { if (node.tagName === 'DETAILS') node.open = true; node = node.parentElement; }
      requestAnimationFrame(() => target.scrollIntoView({behavior:'instant',block:'start'}));
    }
  }
  search.addEventListener('input', filter);
  stage.addEventListener('change', filter);
  letters.forEach(button => button.addEventListener('click', () => { letter = button.dataset.letter; filter(); }));
  document.getElementById('reset').addEventListener('click', reset);
  document.querySelectorAll('[data-reset]').forEach(button => button.addEventListener('click', reset));
  document.querySelectorAll('[data-filter-stage]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault(); history.pushState(null, '', link.getAttribute('href')); showHash();
  }));
  document.querySelectorAll('a[href="#library"]').forEach(link => link.addEventListener('click', reset));
  document.getElementById('expand-courses')?.addEventListener('click', () => items.filter(i => !i.hidden).forEach(i => i.querySelector('.course').open = true));
  document.getElementById('collapse-courses')?.addEventListener('click', () => items.filter(i => !i.hidden).forEach(i => i.querySelector('.course').open = false));
  let printState = [];
  window.addEventListener('beforeprint', () => {
    printState = [...document.querySelectorAll('.deal-stream:not([hidden]), .item:not([hidden]) details')].map(d => [d,d.open]);
    printState.forEach(([d]) => d.open = true);
  });
  window.addEventListener('afterprint', () => { printState.forEach(([d,open]) => d.open = open); printState = []; });
  document.getElementById('print-view')?.addEventListener('click', () => window.print());
  window.addEventListener('hashchange', showHash);
  window.addEventListener('popstate', showHash);
  filter(); showHash();
})();
