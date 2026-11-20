(() => {
  const header = document.querySelector('.marketing-header');
  if (!header) return;
  const toggle = header.querySelector('[aria-controls="marketing-navigation"]');
  const nav = header.querySelector('#marketing-navigation');
  if (!toggle || !nav) return;
  function closeMenu() {
    nav.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    header.querySelectorAll('details[open]').forEach(details => { details.open = false; });
  }
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
    if (!open) header.querySelectorAll('details[open]').forEach(details => { details.open = false; });
  });
  document.addEventListener('click', event => { if (!header.contains(event.target)) closeMenu(); });
  header.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    const details = event.target.closest('details[open]');
    if (details) {
      details.open = false;
      details.querySelector('summary').focus();
    } else if (nav.classList.contains('is-open')) {
      closeMenu();
      toggle.focus();
    }
  });
})();
