(() => {
  const select = document.getElementById('requirement-release-filter');
  if (!select) return;
  const rows = [...document.querySelectorAll('#requirements-table tbody tr')];
  const count = document.getElementById('requirement-release-count');
  function filter() {
    let shown = 0;
    for (const row of rows) {
      const type = row.dataset.releaseType;
      const match = select.value === 'all' ||
        (select.value === 'latest' && type !== 'existing') ||
        (['added', 'revised'].includes(select.value) && type === select.value);
      row.hidden = !match;
      if (match) shown++;
    }
    count.textContent = `${shown} of ${rows.length} requirements shown. Downloads retain their labeled full or October 21 scope.`;
  }
  function revealLinkedRequirement() {
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target?.matches('#requirements-table tbody tr') && target.hidden) {
      select.value = 'all'; filter(); target.scrollIntoView({block: 'center'});
    }
  }
  select.addEventListener('change', filter);
  window.addEventListener('hashchange', revealLinkedRequirement);
  filter(); revealLinkedRequirement();
})();
