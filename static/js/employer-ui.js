/* Navigation and keyboard handling only. Existing page-specific scripts own API actions. */
(() => {
  const sidebar=document.getElementById('employerSidebar');
  const toggle=document.getElementById('employerMenuToggle');
  const backdrop=document.querySelector('.hg-nav-backdrop');
  function closeSidebar(){if(!sidebar)return;sidebar.classList.remove('is-open');toggle?.setAttribute('aria-expanded','false');if(backdrop)backdrop.hidden=true;}
  toggle?.addEventListener('click',()=>{const open=sidebar.classList.toggle('is-open');toggle.setAttribute('aria-expanded',String(open));if(backdrop)backdrop.hidden=!open;});
  document.querySelectorAll('[data-sidebar-close]').forEach(el=>el.addEventListener('click',closeSidebar));
  const focusable='button:not([disabled]),a[href],input:not([disabled]):not([type=hidden]),select:not([disabled]),textarea:not([disabled]),[tabindex="0"]';
  let activeDialog=null,returnFocus=null;
  const visible=el=>!el.classList.contains('hidden')&&getComputedStyle(el).display!=='none';
  function syncDialogs(){
    const next=[...document.querySelectorAll('[role=dialog]')].filter(visible).pop()||null;
    if(next===activeDialog)return;
    if(next){if(!activeDialog)returnFocus=document.activeElement;activeDialog=next;setTimeout(()=>{const first=[...next.querySelectorAll(focusable)].find(el=>el.getClientRects().length);first?.focus();},30);}
    else{activeDialog=null;returnFocus?.focus();returnFocus=null;}
    document.body.style.overflow=next?'hidden':'';
  }
  new MutationObserver(syncDialogs).observe(document.body,{subtree:true,attributes:true,attributeFilter:['class','style']});
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'){
      if(activeDialog){const close=activeDialog.querySelector('[data-dialog-close],button[aria-label^="Close"]');if(close){event.preventDefault();close.click();}}
      else if(sidebar?.classList.contains('is-open')){closeSidebar();toggle?.focus();}
    }
    if(event.key==='Tab'&&activeDialog){const items=[...activeDialog.querySelectorAll(focusable)].filter(el=>el.getClientRects().length);if(!items.length)return;const first=items[0],last=items[items.length-1];if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}}
  });
})();
