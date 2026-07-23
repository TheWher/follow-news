"""Static CSS and JavaScript assets for the follow-news enhanced site.

Kept as Python string constants because the template uses f-string
substitution for CSS variables; the output remains a single self-contained
HTML file.

Extracted from build-enhanced-site.py for modularity.
"""

# ═══════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════

CSS = r"""/* ── Reset & Tokens ── */
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
    --bg:#0a0f1a;
    --card:#121a29;
    --card2:#162032;
    --text:#cbd5e1;
    --text2:#94a3b8;
    --muted:#64748b;
    --accent:#60a5fa;
    --accent2:#3b82f6;
    --success:#34d399;
    --warning:#fbbf24;
    --danger:#f87171;
    --border:rgba(255,255,255,.06);
    --shadow:0 1px 3px rgba(0,0,0,.4);
    --radius:8px;
    --font:'Inter',-apple-system,'Segoe UI','Noto Sans SC',sans-serif;
    --mono:'JetBrains Mono',monospace;
    --transition:150ms ease;
}
html{scroll-behavior:smooth}
body{
    font-family:var(--font);
    font-size:15px;line-height:1.6;
    background:var(--bg);color:var(--text);
    -webkit-font-smoothing:antialiased;
}

/* ── Top Bar (sticky) ── */
.top-bar{
    position:sticky;top:0;z-index:100;
    background:var(--bg);
    border-bottom:1px solid var(--border);
    padding:12px 16px;
    backdrop-filter:blur(12px);
}
.top-bar-inner{
    max-width:1400px;margin:0 auto;
    display:flex;flex-wrap:wrap;gap:10px;align-items:center;
}
.search-wrap{
    flex:1;min-width:200px;max-width:480px;
    position:relative;
}
.search-wrap input{
    width:100%;padding:8px 12px 8px 36px;
    border:1px solid var(--border);border-radius:var(--radius);
    background:var(--card);color:var(--text);
    font-family:var(--font);font-size:14px;
    outline:none;transition:border-color var(--transition),box-shadow var(--transition);
}
.search-wrap input:focus{
    border-color:var(--accent);
    box-shadow:0 0 0 3px rgba(96,165,250,.15);
}
.search-wrap input::placeholder{color:var(--muted)}
.search-icon{
    position:absolute;left:10px;top:50%;transform:translateY(-50%);
    color:var(--muted);font-size:16px;pointer-events:none;
}
.search-clear{
    position:absolute;right:8px;top:50%;transform:translateY(-50%);
    background:none;border:none;color:var(--muted);cursor:pointer;
    font-size:16px;display:none;padding:2px 6px;border-radius:4px;
}
.search-clear:hover{color:var(--text);background:var(--card2)}
.search-clear.visible{display:block}
.search-info{
    font-size:12px;color:var(--muted);white-space:nowrap;
}

/* ── Filter Chips ── */
.chips{
    display:flex;flex-wrap:nowrap;gap:6px;
    overflow-x:auto;scrollbar-width:none;
    padding:2px 0;
}
.chips::-webkit-scrollbar{display:none}
.chip{
    padding:5px 12px;border-radius:20px;
    font-size:13px;font-family:var(--font);
    border:1px solid var(--border);background:var(--card);
    color:var(--text2);cursor:pointer;
    white-space:nowrap;transition:all var(--transition);
    user-select:none;
}
.chip:hover{border-color:var(--muted);color:var(--text)}
.chip.active{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:500}

/* ── Container ── */
.container{max-width:1400px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:22px;font-weight:600;margin-bottom:4px;color:var(--text)}
.delayed{color:var(--warning);font-size:13px;margin-bottom:16px}

/* ── Date Summary ── */
.date-summary{
    display:flex;flex-wrap:wrap;gap:12px;align-items:center;
    margin-bottom:20px;font-size:13px;color:var(--text2);
}
.date-summary strong{color:var(--text)}

/* ── Archive Bar ── */
.archive-bar{
    display:flex;gap:6px;margin-bottom:20px;padding-bottom:14px;
    border-bottom:1px solid var(--border);
    overflow-x:auto;scroll-snap-type:x proximity;
    scrollbar-width:thin;scrollbar-color:var(--muted) transparent;
}
.archive-bar a{
    flex-shrink:0;scroll-snap-align:start;
    font-size:13px;color:var(--muted);text-decoration:none;
    padding:4px 10px;border-radius:var(--radius);
    font-family:var(--font);transition:all var(--transition);
}
.archive-bar a:hover{color:var(--accent);background:var(--card)}
.archive-bar a.active{color:var(--accent);background:var(--card);font-weight:600}

/* ── Sections ── */
.section{margin-bottom:28px}
.section.hidden{display:none}
.section-title{
    font-size:17px;font-weight:600;margin-bottom:12px;
    color:var(--text);display:flex;align-items:center;gap:8px;
}
.section-count{font-size:13px;font-weight:400;color:var(--muted)}

/* ── Cards ── */
.cards{display:flex;flex-direction:column;gap:12px}
.card{
    background:var(--card);border-radius:var(--radius);padding:16px;
    box-shadow:var(--shadow);cursor:pointer;
    transition:background var(--transition),opacity var(--transition),border-color var(--transition);
    position:relative;border-left:3px solid transparent;
}
.card:hover{background:var(--card2)}
.card.hidden-by-search{display:none}

/* Read state */
.card.read{
    opacity:.55;
    border-left-color:var(--muted);
}
.card.read:hover{opacity:.75}

/* Card header */
.card-header{
    display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;
}
.card-title{
    flex:1;font-size:16px;font-weight:600;color:var(--accent);
    line-height:1.4;
}
.card-body{font-size:15px;color:var(--text);margin-bottom:6px;line-height:1.6}
.card-insight{
    font-size:14px;color:var(--text2);margin-bottom:8px;
    padding:8px 12px;border-radius:6px;
    background:rgba(96,165,250,.06);
    border-left:2px solid var(--accent);
}

/* Card actions */
.card-actions{
    display:flex;flex-wrap:wrap;gap:8px;align-items:center;
    margin-top:4px;
}
.card-btn{
    display:inline-flex;align-items:center;gap:4px;
    padding:6px 14px;border-radius:6px;
    font-size:13px;font-family:var(--font);font-weight:500;
    text-decoration:none;cursor:pointer;
    transition:all var(--transition);position:relative;z-index:2;
    user-select:none;
}
.card-btn-primary{
    background:var(--accent);color:#fff;border:1px solid var(--accent);
}
.card-btn-primary:hover{
    background:var(--accent2);border-color:var(--accent2);
}

/* Bookmark */
.card-bookmark{
    flex-shrink:0;
    background:none;border:none;color:var(--muted);cursor:pointer;
    font-size:18px;padding:4px 6px;border-radius:6px;
    transition:all var(--transition);position:relative;z-index:2;
    line-height:1;
}
.card-bookmark:hover{color:var(--warning);background:rgba(251,191,36,.1)}
.card-bookmark.bookmarked{color:var(--warning)}
.card-bookmark.bookmarked .bm-icon::before{content:'★'}

/* Badges */
.card-stars{font-size:12px;color:var(--success);font-weight:500}
.card-domain{
    font-size:11px;color:var(--muted);font-family:var(--mono);
    padding:2px 8px;border-radius:4px;background:var(--card2);
}
.card-read-badge{
    font-size:12px;color:var(--success);
    display:none;align-items:center;gap:3px;
    margin-left:auto;
}
.card.read .card-read-badge{display:inline-flex}

/* ── No results ── */
.no-results{
    display:none;text-align:center;padding:48px 16px;color:var(--muted);
}
.no-results.visible{display:block}
.no-results-icon{font-size:48px;margin-bottom:12px}

/* ── Footer ── */
footer{
    text-align:center;color:var(--muted);font-size:13px;
    margin-top:40px;padding-top:16px;border-top:1px solid var(--border);
}

/* ── Back to top ── */
#back-top{
    position:fixed;bottom:24px;right:24px;
    width:40px;height:40px;border-radius:50%;
    background:var(--card);color:var(--muted);
    border:1px solid var(--muted);cursor:pointer;
    display:none;align-items:center;justify-content:center;
    font-size:18px;z-index:100;transition:all var(--transition);
}
#back-top:hover{color:var(--accent);border-color:var(--accent)}
#back-top.visible{display:flex}

/* ── Toast ── */
.toast{
    position:fixed;bottom:80px;left:50%;transform:translateX(-50%);
    background:var(--card);color:var(--text);
    padding:8px 20px;border-radius:20px;font-size:13px;
    box-shadow:0 4px 12px rgba(0,0,0,.5);
    z-index:200;opacity:0;transition:opacity .2s;
    pointer-events:none;
}
.toast.show{opacity:1}

/* ── Responsive ── */
@media(max-width:768px){
    .top-bar{padding:10px 12px}
    .top-bar-inner{gap:8px}
    .search-wrap{max-width:100%}
    .container{padding:16px 12px}
    h1{font-size:19px}
    .section-title{font-size:15px}
    .card-title{font-size:15px}
    .card-body{font-size:14px}
    .card{padding:14px}
    .card-actions{gap:6px}
    .card-btn{padding:5px 12px;font-size:12px}
    .chips{gap:4px}
    .chip{padding:4px 10px;font-size:12px}
    .archive-bar a{font-size:12px;padding:3px 8px}
}
@media(max-width:480px){
    h1{font-size:17px}
    .card{padding:12px;border-radius:6px}
    .card-title{font-size:14px}
    .card-body{font-size:13px}
    .card-insight{font-size:13px;padding:6px 10px}
    .card-btn{padding:5px 10px;font-size:11px}
    .section{margin-bottom:20px}
    .cards{gap:8px}
}
"""


# ═══════════════════════════════════════════════════════════
#  JavaScript
# ═══════════════════════════════════════════════════════════

JS = r"""
const DIGEST_DATE = "{date_str}";
const ALL_ARTICLES = {articles_json};

// ── localStorage helpers ──
const LS_BOOKMARKS = 'fn_bookmarks';
const LS_READ = 'fn_read';

function getLS(key) {
    try { return new Set(JSON.parse(localStorage.getItem(key) || '[]')); }
    catch { return new Set(); }
}
function setLS(key, set) {
    try { localStorage.setItem(key, JSON.stringify([...set])); } catch {}
}
function inLS(key, url) { return getLS(key).has(url); }
function toggleLS(key, url) {
    const s = getLS(key);
    if (s.has(url)) { s.delete(url); } else { s.add(url); }
    setLS(key, s);
    return s.has(url);
}

// ── State ──
let activeFilter = 'all';
let searchQuery = '';

// ── DOM refs ──
const searchInput = document.getElementById('search-input');
const searchClear = document.getElementById('search-clear');
const searchInfo = document.getElementById('search-info');
const filterChips = document.getElementById('filter-chips');
const noResults = document.getElementById('no-results');
const toast = document.getElementById('toast');
const backTop = document.getElementById('back-top');

// ── Card click → open URL ──
document.querySelectorAll('.card[data-href]').forEach(card => {
    card.addEventListener('click', function(e) {
        if (e.target.closest('a') || e.target.closest('button') || e.target.closest('.card-bookmark')) return;
        const url = this.dataset.href;
        if (url) {
            markRead(this.dataset.url || url);
            window.open(url, '_blank', 'noopener');
        }
    });
});

// ── Bookmark buttons ──
document.querySelectorAll('.card-bookmark').forEach(btn => {
    const url = btn.dataset.url;
    if (inLS(LS_BOOKMARKS, url)) btn.classList.add('bookmarked');
    btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const isNow = toggleLS(LS_BOOKMARKS, url);
        this.classList.toggle('bookmarked', isNow);
        showToast(isNow ? '已收藏 ★' : '已取消收藏');
        updateCounts();
        applyAllFilters();
    });
});

// ── Read tracking ──
function markRead(url) {
    if (!inLS(LS_READ, url)) {
        getLS(LS_READ).add(url);
        setLS(LS_READ, getLS(LS_READ));
    }
    updateReadUI();
    updateCounts();
}

function updateReadUI() {
    const readSet = getLS(LS_READ);
    document.querySelectorAll('.card[data-url]').forEach(card => {
        if (readSet.has(card.dataset.url)) card.classList.add('read');
    });
}

// ── Filter chips ──
filterChips.addEventListener('click', function(e) {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    const filter = chip.dataset.filter;

    if (chip.classList.contains('active') && filter !== 'all') {
        activeFilter = 'all';
    } else {
        activeFilter = filter;
    }

    updateChipUI();
    applyAllFilters();
});

function updateChipUI() {
    filterChips.querySelectorAll('.chip').forEach(c => {
        c.classList.toggle('active', c.dataset.filter === activeFilter);
    });
}

// ── Search ──
let searchTimer;
searchInput.addEventListener('input', function() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
        searchQuery = this.value.trim().toLowerCase();
        searchClear.classList.toggle('visible', searchQuery.length > 0);
        applyAllFilters();
    }, 150);
});
searchClear.addEventListener('click', function() {
    searchInput.value = '';
    searchQuery = '';
    searchClear.classList.remove('visible');
    searchInput.focus();
    applyAllFilters();
});

// ── Apply all filters ──
function applyAllFilters() {
    const readSet = getLS(LS_READ);
    const bookmarkSet = getLS(LS_BOOKMARKS);
    let visibleCount = 0;
    let totalInFilter = 0;

    document.querySelectorAll('.section').forEach(section => {
        const cat = section.dataset.category;
        let sectionHasVisible = false;

        section.querySelectorAll('.card').forEach(card => {
            const url = card.dataset.url;
            let show = true;

            if (activeFilter === 'bookmarks') {
                show = bookmarkSet.has(url);
            } else if (activeFilter === 'unread') {
                show = !readSet.has(url);
            } else if (activeFilter !== 'all') {
                show = (cat === activeFilter);
            }

            if (show && searchQuery) {
                const title = (card.querySelector('.card-title')?.textContent || '').toLowerCase();
                const body = (card.querySelector('.card-body')?.textContent || '').toLowerCase();
                const insight = (card.querySelector('.card-insight')?.textContent || '').toLowerCase();
                const allText = title + ' ' + body + ' ' + insight;
                const terms = searchQuery.split(/\s+/).filter(Boolean);
                show = terms.every(t => allText.includes(t));
            }

            if (show) {
                card.classList.remove('hidden-by-search');
                visibleCount++;
                sectionHasVisible = true;
            } else {
                card.classList.add('hidden-by-search');
            }
            totalInFilter++;
        });

        section.classList.toggle('hidden', !sectionHasVisible);
    });

    noResults.classList.toggle('visible', visibleCount === 0 && totalInFilter > 0);

    if (searchQuery) {
        searchInfo.textContent = `找到 ${visibleCount} 篇`;
    } else {
        searchInfo.textContent = '';
    }

    updateCounts();
}

// ── Counts ──
function updateCounts() {
    const visible = document.querySelectorAll('.card:not(.hidden-by-search)').length;
    const total = document.querySelectorAll('.card').length;
    const bookmarkN = getLS(LS_BOOKMARKS).size;
    const readN = getLS(LS_READ).size;
    const unreadN = total - readN;

    document.getElementById('total-count').innerHTML = `<strong>共 ${total} 篇</strong>`;
    document.getElementById('visible-count').textContent = visible !== total ? `显示 ${visible} 篇` : '';
    document.getElementById('bookmark-count').textContent = bookmarkN > 0 ? `📌 ${bookmarkN} 书签` : '';
    document.getElementById('unread-count').textContent = unreadN > 0 ? `👁 ${unreadN} 未读` : '';
    document.getElementById('footer-stats').textContent =
        `${total} articles · ${bookmarkN} bookmarked · ${readN} read · built ${new Date().toISOString().slice(0,10)}`;

    const bookmarkChip = filterChips.querySelector('[data-filter="bookmarks"]');
    if (bookmarkChip) bookmarkChip.textContent = `📌 书签 (${bookmarkN})`;
    const unreadChip = filterChips.querySelector('[data-filter="unread"]');
    if (unreadChip) unreadChip.textContent = `👁 未读 (${unreadN})`;
}

// ── Toast ──
let toastTimer;
function showToast(msg) {
    clearTimeout(toastTimer);
    toast.textContent = msg;
    toast.classList.add('show');
    toastTimer = setTimeout(() => toast.classList.remove('show'), 1800);
}

// ── Back to top ──
window.addEventListener('scroll', function() {
    backTop.classList.toggle('visible', window.scrollY > 500);
});

// ── Keyboard shortcuts ──
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey && e.key === 'k') || (e.key === '/' && !e.ctrlKey && !e.metaKey && document.activeElement === document.body)) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
    }
    if (e.key === 'Escape' && document.activeElement === searchInput) {
        searchInput.value = '';
        searchQuery = '';
        searchClear.classList.remove('visible');
        searchInput.blur();
        applyAllFilters();
    }
});

// ── Init ──
updateReadUI();
updateCounts();
"""
