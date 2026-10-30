document.documentElement.classList.add('js');

const menu = document.querySelector('.menu');
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menu?.open) {
    menu.open = false;
    menu.querySelector('summary').focus();
  }
});
document.addEventListener('click', event => {
  if (menu?.open && !menu.contains(event.target)) menu.open = false;
});

const searchForm = document.querySelector('.search');
const searchInput = document.querySelector('#site-search');
const results = document.querySelector('.search-results');
const searchStatus = document.querySelector('.search-status');
let searchIndex;
let searchRevision = 0;
async function searchPages() {
  const revision = ++searchRevision;
  const query = searchInput.value.trim().toLocaleLowerCase('en-AU');
  results.replaceChildren();
  if (!query) { searchStatus.textContent = ''; return; }
  try {
    searchStatus.textContent = 'Searching…';
    searchIndex ??= fetch('assets/search-index.json').then(response => {
      if (!response.ok) throw new Error('Search index unavailable');
      return response.json();
    });
    const pages = await searchIndex;
    if (revision !== searchRevision) return;
    const words = query.split(/\s+/);
    const found = pages.filter(page => words.every(word => (page.title + ' ' + page.text).toLocaleLowerCase('en-AU').includes(word)));
    for (const page of found) {
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = page.url;
      link.textContent = page.title;
      item.append(link);
      results.append(item);
    }
    searchStatus.textContent = found.length ? `${found.length} reading ${found.length === 1 ? 'page' : 'pages'} found.` : 'No page matches. Try a shorter phrase, or browse the site map.';
  } catch {
    if (revision === searchRevision) searchStatus.textContent = 'Search is unavailable. Every page is linked in the menu and site map.';
  }
}
searchForm?.addEventListener('submit', event => { event.preventDefault(); searchPages(); });
searchInput?.addEventListener('input', searchPages);

const chapters = [...document.querySelectorAll('.document-chapter')];
document.querySelector('#open-chapters')?.addEventListener('click', () => chapters.forEach(chapter => { chapter.open = true; }));
document.querySelector('#close-chapters')?.addEventListener('click', () => chapters.forEach(chapter => { chapter.open = false; }));
function openHashTarget() {
  if (!location.hash) return;
  let target;
  try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch { return; }
  if (!target) return;
  const chapter = target.closest('.document-chapter');
  if (chapter) {
    chapter.open = true;
    requestAnimationFrame(() => target.scrollIntoView());
  }
}
window.addEventListener('hashchange', openHashTarget);
openHashTarget();

const draft = document.querySelector('#interest-draft');
if (draft) {
  const preview = document.querySelector('#draft-preview');
  const status = document.querySelector('#draft-status');
  function draftText() {
    const values = new FormData(draft);
    const text = String(values.get('note') || '').trim();
    return 'Expression of interest: Aura of Intelligence for disaster resilience and recovery\n\n' +
      'Interest: ' + values.get('interest') + '\n' +
      (String(values.get('place') || '').trim() ? 'Place or setting: ' + String(values.get('place')).trim() + '\n' : '') +
      '\nWhat I would like to explore:\n' + (text || '[Add a useful question or possibility.]') +
      '\n\nThis is early interest in developing a suitable scope, shared targets and mutually acceptable terms.';
  }
  function updateDraft() { preview.textContent = draftText(); status.textContent = ''; }
  draft.addEventListener('submit', event => event.preventDefault());
  draft.addEventListener('input', updateDraft);
  draft.addEventListener('change', updateDraft);
  document.querySelector('#copy-draft').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(draftText());
      status.textContent = 'Copied. Choose your own sharing route.';
    } catch {
      status.textContent = 'Select and copy the note below, or download the text file.';
      const selection = window.getSelection();
      const range = document.createRange(); range.selectNodeContents(preview);
      selection.removeAllRanges(); selection.addRange(range);
    }
  });
  document.querySelector('#download-draft').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([draftText()], {type:'text/plain;charset=utf-8'}));
    const link = document.createElement('a'); link.href = url;
    link.download = 'Aura_Disaster_Expression_of_Interest.txt'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    status.textContent = 'Text file prepared. Nothing was submitted.';
  });
  updateDraft();
}
