'use strict';
(() => {
  const contrast = document.querySelector('.contrast-toggle');
  const applyContrast = enabled => {
    document.documentElement.classList.toggle('high-contrast', enabled);
    contrast?.setAttribute('aria-pressed', String(enabled));
  };
  let highContrast = false;
  try { highContrast = localStorage.getItem('recipe-high-contrast') === 'true'; } catch (_) { /* Storage is optional. */ }
  applyContrast(highContrast);
  if (contrast) {
    contrast.hidden = false;
    contrast.addEventListener('click', () => {
      highContrast = !highContrast;
      applyContrast(highContrast);
      try { localStorage.setItem('recipe-high-contrast', String(highContrast)); } catch (_) { /* Storage is optional. */ }
    });
  }
  const print = document.querySelector('.print-button');
  if (print) { print.hidden = false; print.addEventListener('click', () => window.print()); }
  const search = document.querySelector('#search');
  if (!search) return;
  const cards = [...document.querySelectorAll('.recipe-card')];
  const groups = [...document.querySelectorAll('.letter-group')];
  const filters = [...document.querySelectorAll('[data-category]')];
  const count = document.querySelector('#result-count');
  const clear = document.querySelector('#clear-search');
  const params = new URLSearchParams(location.search);
  let category = params.get('category') || '';
  if (!filters.some(button => button.dataset.category === category)) category = '';
  search.value = params.get('q') || '';
  document.querySelector('.search-wrap').hidden = false;
  document.querySelector('.filters').hidden = false;
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim();
  function update() {
    const query = normalize(search.value);
    let visible = 0;
    for (const card of cards) {
      const matches = normalize(card.dataset.title).includes(query) && (!category || JSON.parse(card.dataset.categories).includes(category));
      card.hidden = !matches;
      if (matches) visible++;
    }
    for (const group of groups) {
      group.hidden = ![...group.querySelectorAll('.recipe-card')].some(card => !card.hidden);
      const jump = document.querySelector(`.alphabet a[href="#${group.id}"]`);
      if (jump) jump.hidden = group.hidden;
    }
    for (const button of filters) button.setAttribute('aria-pressed', String(button.dataset.category === category));
    count.textContent = `${visible} ${visible === 1 ? 'recipe' : 'recipes'}${category ? ` · ${category}` : ''} · A–Z`;
    clear.hidden = !search.value;
    document.querySelector('#empty-state').hidden = visible !== 0;
    const url = new URL(location.href);
    if (search.value) url.searchParams.set('q', search.value); else url.searchParams.delete('q');
    if (category) url.searchParams.set('category', category); else url.searchParams.delete('category');
    history.replaceState(null, '', url);
  }
  search.addEventListener('input', update);
  clear.addEventListener('click', () => { search.value = ''; update(); search.focus(); });
  for (const button of filters) button.addEventListener('click', () => { category = button.dataset.category; update(); });
  document.querySelector('#reset-filters').addEventListener('click', () => { category = ''; search.value = ''; update(); search.focus(); });
  update();
})();
