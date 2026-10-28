(() => {
  'use strict';
  const cards = [...document.querySelectorAll('[data-process]')];
  const groups = [...document.querySelectorAll('[data-phase-group]')];
  const search = document.getElementById('process-search');
  const phase = document.getElementById('process-phase');
  const count = document.getElementById('process-count');
  const normalized = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const texts = new Map(cards.map(card => [card, normalized(card.textContent)]));
  function filter() {
    const words = normalized(search.value).trim().split(/\s+/).filter(Boolean);
    let shown = 0;
    cards.forEach(card => {
      card.hidden = !(words.every(word => texts.get(card).includes(word)) &&
        (phase.value === 'all' || phase.value === card.dataset.phase));
      if (!card.hidden) shown++;
    });
    groups.forEach(group => {
      group.hidden = ![...group.querySelectorAll('[data-process]')].some(card => !card.hidden);
      if (!group.hidden && (words.length || phase.value !== 'all')) group.open = true;
    });
    count.textContent = `${shown} of ${cards.length} processes shown. The question register retains all 49 open questions.`;
    document.getElementById('process-empty').hidden = shown > 0;
  }
  function reset() {search.value = ''; phase.value = 'all'; filter();}
  function revealHash() {
    let id;
    try {id = decodeURIComponent(location.hash.slice(1));} catch {return;}
    const target = document.getElementById(id);
    if (!target) return;
    if (target.closest('#process-library')) reset();
    let node = target;
    while (node && node !== document.body) {
      if (node.tagName === 'DETAILS') node.open = true;
      node = node.parentElement;
    }
    requestAnimationFrame(() => target.scrollIntoView({behavior:'instant', block:'start'}));
  }
  search.addEventListener('input', filter);
  phase.addEventListener('change', filter);
  document.getElementById('reset-processes').addEventListener('click', reset);
  document.getElementById('expand-processes').addEventListener('click', () => {
    groups.filter(group => !group.hidden).forEach(group => group.open = true);
    cards.filter(card => !card.hidden).forEach(card => card.open = true);
  });
  document.getElementById('collapse-processes').addEventListener('click', () => {
    cards.forEach(card => card.open = false); groups.forEach(group => group.open = false);
  });
  document.getElementById('copy-questions').addEventListener('click', async () => {
    const content = [...document.querySelectorAll('.question-register [data-question]')]
      .map(item => `${item.dataset.question}: ${item.querySelector('p').textContent}`).join('\n\n');
    const status = document.getElementById('copy-status');
    try {await navigator.clipboard.writeText(content); status.textContent = 'Copied all 49 questions. Reply using the question IDs.';}
    catch {
      const fallback = document.getElementById('question-copy-fallback');
      fallback.hidden = false; fallback.value = content; fallback.focus(); fallback.select();
      status.textContent = 'Select and copy the questions below, then reply using the question IDs.';
    }
  });
  let printState = [];
  window.addEventListener('beforeprint', () => {
    printState = [...document.querySelectorAll('details')].filter(detail => !detail.hidden && !detail.closest('[hidden]')).map(detail => [detail, detail.open]);
    printState.forEach(([detail]) => detail.open = true);
  });
  window.addEventListener('afterprint', () => {printState.forEach(([detail, open]) => detail.open = open); printState = [];});
  document.getElementById('print-processes').addEventListener('click', () => window.print());
  window.addEventListener('hashchange', revealHash);
  window.addEventListener('popstate', revealHash);
  filter(); revealHash();
})();
