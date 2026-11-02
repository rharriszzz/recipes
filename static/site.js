'use strict';
// Recipe-page enhancements only. The compact homepage needs no JavaScript.
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
})();
