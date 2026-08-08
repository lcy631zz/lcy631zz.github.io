/* Main JS: language switcher, scroll, lightbox, content rendering */
let DATA = null, lang = 'zh-Hans';

/* Detect current page from URL */
function getPage() {
    const p = window.location.pathname.replace(/\/$/, '') || '/';
    if (p === '/') return 'home';
    if (p === '/about') return 'about';
    if (p === '/blog') return 'blog';
    if (p === '/projects') return 'projects';
    if (p === '/yin') return 'yin';
    if (p === '/xing') return 'xing';
    if (p === '/zhai') return 'zhai';
    if (p.startsWith('/blog/')) return 'blog-single';
    if (p.startsWith('/projects/')) return 'project-single';
    if (p.startsWith('/zhai/')) return 'zhai-single';
    return 'other';
}

function $(id) { return document.getElementById(id); }

function loadContent() {
    loadLang();
    try {
        DATA = window.I18N;
    } catch (e) {
        console.error('[i18n] Failed to load data:', e);
        return;
    }
    try {
        render();
    } catch (e) {
        console.error('[render] Error:', e);
    }
}

function t(k) { return DATA?.[lang]?.[k] ?? ''; }
function na() { return lang === 'en' ? 'N/A' : '无'; }

/* Convert relative image path to absolute site-root path */
function absPath(p) {
    if (!p) return '';
    if (p.startsWith('/') || p.startsWith('http') || p.startsWith('data:')) return p;
    return '/' + p;
}

/* Open lightbox */
function openLightbox(img, cap) {
    const lbImg = $('lbImg'), lbCap = $('lbCap'), lb = $('lightbox');
    if (lbImg) lbImg.src = img || '';
    if (lbCap) lbCap.textContent = cap || '';
    if (lb) lb.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function render() {
    if (!DATA) return;
    const d = DATA[lang];
    if (!d) return;
    const page = getPage();

    /* Site name (all pages) */
    const sn = $('siteName');
    if (sn) sn.textContent = d.site_name;

    /* Homepage hero elements */
    if (page === 'home') {
        setText('hBadge', d.hero?.badge);
        setText('hT1', d.hero?.title_1);
        setText('hTHL', d.hero?.title_hl);
        setText('hT2', d.hero?.title_2);
        setText('hT3', d.hero?.title_3);
        setText('hTHL2', d.hero?.title_hl2);
        setText('hT4', d.hero?.title_4);
        setText('hSub', d.hero?.subtitle);
        setText('sHint', lang === 'en' ? 'Scroll Down' : '向下探索');
        setText('hubAboutTitle', d.about?.name);
        setText('hubArtTitle', d.articles?.title);
        setText('hubArtDesc', d.articles?.hub_desc || d.articles?.desc);
        setText('hubProjTitle', d.projects?.title);
        setText('hubProjDesc', d.projects?.hub_desc || d.projects?.desc);
        setText('hubZhaiTitle', d.zhai?.title);
        setText('hubZhaiDesc', d.zhai?.hub_desc || d.zhai?.desc);
        setText('hubYinTitle', d.yin?.title);
        setText('hubYinDesc', d.yin?.hub_desc || d.yin?.desc);
        setText('hubXingTitle', d.xing?.title);
        setText('hubXingDesc', d.xing?.hub_desc || d.xing?.desc);
        requestAnimationFrame(() => {
            const hero = $('hero');
            if (hero) hero.querySelectorAll('.fi').forEach(el => el.classList.add('v'));
        });
    }

    /* About page */
    if (page === 'about') {
        const a = d.about;
        setText('aName', a?.name);
        setText('aRole', a?.role);
        setText('aIntroTitle', a?.intro_title);
        setText('aIntro', a?.intro_text);
        setText('aInfoTitle', a?.info_title);
        setText('aInfo', a?.info_text);
    }

    /* Blog section page */
    if (page === 'blog') {
        setText('pageDesc', d.articles?.desc);
    }

    /* Projects section page */
    if (page === 'projects') {
        setText('pageDesc', d.projects?.desc);
    }

    /* Yin section page */
    if (page === 'yin') {
        setText('pageDesc', d.yin?.desc);
        const yqt = $('yQuoteText'), yqa = $('yQuoteAuthor'), yq = $('yinQuote');
        if (yqt) yqt.textContent = d.yin?.quote || '';
        if (yqa) yqa.textContent = d.yin?.quote_author || '';
        if (yq) yq.style.display = d.yin?.quote ? 'block' : 'none';
        renderYinGrid();
    }

    /* Xing section page */
    if (page === 'xing') {
        setText('pageDesc', d.xing?.desc);
        renderXingGrid();
    }

    /* Zhai section page */
    if (page === 'zhai') {
        setText('pageDesc', d.zhai?.desc);
        renderZhaiList();
    }

    /* Footer (all pages) */
    setText('footer', d?.footer);

    /* Animate .fi elements on all pages */
    requestAnimationFrame(() => {
        document.querySelectorAll('.fi:not(.v)').forEach(el => el.classList.add('v'));
    });

    /* Language switcher button states */
    document.querySelectorAll('.lang-btn').forEach(b => {
        b.classList.toggle('on', b.dataset.lang === lang);
    });

    /* Navigation active state */
    setNavActive(page);
}

/* Helper: safely set element text */
function setText(id, val) {
    const el = $(id);
    if (el && val !== undefined) el.textContent = val;
}

/* Render yin photo grid */
function renderYinGrid() {
    const yg = $('yinGrid');
    if (!yg) return;
    if (!window.YIN || !window.YIN.items || !window.YIN.items.length) {
        yg.innerHTML = '<div class="empty"><div class="empty-icon">🌿</div>' + na() + '</div>';
        return;
    }
    yg.innerHTML = window.YIN.items.map(y => {
        const cap = (y.caption || '').replace(/'/g, "\\'");
        const src = absPath(y.img);
        return '<div class="yin-item fi" onclick="openLightbox(\'' + src + '\',\'' + cap + '\')">' +
            '<img src="' + src + '" alt="' + (y.caption || '') + '" loading="lazy">' +
            (y.caption ? '<div class="yin-caption">' + y.caption + '</div>' : '') +
            '</div>';
    }).join('');
    requestAnimationFrame(() => {
        yg.querySelectorAll('.fi').forEach(el => el.classList.add('v'));
    });
}

/* Render xing travel grid */
function renderXingGrid() {
    const xg = $('xingGrid');
    if (!xg) return;
    if (!window.XING || !window.XING.items || !window.XING.items.length) {
        xg.innerHTML = '<div class="empty"><div class="empty-icon">✈️</div>' + na() + '</div>';
        return;
    }
    xg.innerHTML = window.XING.items.map(x => {
        const cap = (x.caption || '').replace(/'/g, "\\'");
        const src = absPath(x.img);
        return '<div class="xing-item fi" onclick="openLightbox(\'' + src + '\',\'' + cap + '\')">' +
            '<img src="' + src + '" alt="' + (x.caption || '') + '" loading="lazy">' +
            (x.place ? '<div class="xing-place">' + x.place + '</div>' : '') +
            (x.caption ? '<div class="xing-caption">' + x.caption + '</div>' : '') +
            '</div>';
    }).join('');
    requestAnimationFrame(() => {
        xg.querySelectorAll('.fi').forEach(el => el.classList.add('v'));
    });
}

/* Escape single quotes for use in HTML onclick attributes */
function sqEscape(s) { return (s || '').replace(/'/g, String.fromCharCode(92, 39)); }

/* Render zhai quote list */
function renderZhaiList() {
    const zl = $('zhaiList');
    if (!zl) return;
    if (!window.ZHAI || !window.ZHAI.items || !window.ZHAI.items.length) {
        zl.innerHTML = '<div class="empty"><div class="empty-icon">🍒</div>' + na() + '</div>';
        return;
    }
    zl.innerHTML = window.ZHAI.items.map((z, i) => {
        const quote = sqEscape(z.quote || '');
        const source = z.source ? '<cite>—— ' + z.source + '</cite>' : '';
        const isPoetry = z.poetry;
        let html = '<div class="zhai-item fi ' + (isPoetry ? 'zhai-poetry-card' : '') + '" onclick="openZhaiModal(' + i + ')">';
        if (z.img) {
            const img = absPath(z.img);
            const ie = sqEscape(img);
            const se = sqEscape(z.source || '');
            html += '<img class="zhai-img" src="' + img + '" alt="' + (z.source || '') + '" onclick="event.stopPropagation();openLightbox(\'' + ie + '\',\'' + se + '\')">';
        }
        if (isPoetry) {
            // Poetry: show each stanza (split by \n) as a separate line
            const stanzas = quote.split('\n').filter(s => s.trim());
            html += '<div class="zhai-poetry-body">';
            stanzas.forEach((s, si) => {
                html += '<div class="zhai-poetry-line" style="margin-bottom:' + (si < stanzas.length - 1 ? '18px' : '0') + '">' + s.trim() + '</div>';
            });
            html += '</div>';
            if (source) html += '<div class="zhai-poetry-source">' + source + '</div>';
            if (z.note) html += '<div class="zhai-note">' + z.note + '</div>';
        } else {
            html += '<div class="zhai-quote">"' + quote + '"</div>' +
source +
                (z.note ? '<div class="zhai-note">' + z.note + '</div>' : '');
        }
        html += '</div>';
        return html;
    }).join('');
    requestAnimationFrame(() => {
        zl.querySelectorAll('.fi').forEach(el => el.classList.add('v'));
    });
}

/* Open a zhai quote in modal */
function openZhaiModal(i) {
    const z = window.ZHAI.items[i];
    if (!z) return;
    const quote = (z.quote || '').replace(/'/g, "\\'");
    const source = z.source || '';
    const note = z.note || '';
    document.getElementById('mTitle').textContent = source || (lang === 'en' ? 'Excerpt' : '摘抄');
    if (z.poetry) {
        const stanzas = quote.split('\n').filter(s => s.trim());
        let body = '<div style="text-align:center;padding:20px 0">';
        body += '<div class="zhai-poetry-body">';
        stanzas.forEach(function(stanza, si) {
            body += '<div class="zhai-poetry-line" style="margin-bottom:' + (si < stanzas.length - 1 ? '18px' : '0') + '">' + stanza.trim() + '</div>';
        });
        body += '</div></div>';
        if (source) {
            body += '<p style="text-align:center;color:var(--purple);font-size:1rem;margin-top:16px">—— ' + source + '</p>';
        }
        if (z.img) {
            const img = absPath(z.img);
            const ie = sqEscape(img);
            const se = sqEscape(source || '');
            body += '<div style="margin-top:16px;text-align:center"><img src="' + img + '" style="max-width:100%;border-radius:var(--r-s);cursor:pointer" onclick="openLightbox(\'' + ie + '\',\'' + se + '\')"></div>';
        }
        if (note) {
            body += '<p style="color:var(--text3);font-size:.88rem;margin-top:12px;text-align:center">' + note + '</p>';
        }
    } else {
        let body = '<blockquote style="font-size:1.3rem;line-height:2;font-style:italic;color:var(--text);border-left:3px solid var(--red);padding:16px 24px;margin:0;background:var(--red-light);border-radius:0 var(--r-s) var(--r-s) 0">';
        body += '“' + quote + '”</blockquote>';
        if (z.img) {
            const img = absPath(z.img);
            const ie = sqEscape(img);
            const se = sqEscape(source || '');
            body += '<div style="margin-top:16px;text-align:center"><img src="' + img + '" style="max-width:100%;border-radius:var(--r-s);cursor:pointer" onclick="openLightbox(\'' + ie + '\',\'' + se + '\')"></div>';
        }
        if (note) {
            body += '<p style="color:var(--text3);font-size:.88rem;margin-top:12px">' + note + '</p>';
        }
    }
    document.getElementById('mMeta').innerHTML = '';
    document.getElementById('mBody').innerHTML = body;
    document.getElementById('artModal').classList.add('show');
    document.body.style.overflow = 'hidden';
}

/* Highlight active nav link */
function setNavActive(page) {
    const nav = document.querySelector('.nav-links');
    if (!nav) return;
    const map = {
        'home': '',
        'about': '/about/',
        'blog': '/blog/',
        'projects': '/projects/',
        'yin': '/yin/',
        'xing': '/xing/',
        'zhai': '/zhai/',
        'blog-single': '/blog/',
        'project-single': '/projects/',
        'zhai-single': '/zhai/'
    };
    const target = map[page] || '';
    nav.querySelectorAll('a').forEach(a => {
        a.classList.toggle('on', a.getAttribute('href') === target);
    });
}

/* Language switcher */
function setLang(l) {
    lang = l;
    document.documentElement.lang = l;
    try { localStorage.setItem('site-lang', l); } catch(e) {}
    render();
}

/* Load saved language */
function loadLang() {
    try {
        const saved = localStorage.getItem('site-lang');
        if (saved && (saved === 'zh-Hans' || saved === 'zh-Hant' || saved === 'en')) {
            lang = saved;
            document.documentElement.lang = lang;
        }
    } catch(e) {}
}

/* Modal (kept for backward compat) */
function closeModal() {
    const m = $('artModal');
    if (m) m.classList.remove('show');
    document.body.style.overflow = '';
}
function closeLightbox() {
    const lb = $('lightbox');
    if (lb) lb.classList.remove('show');
    document.body.style.overflow = '';
}

const artModal = $('artModal');
if (artModal) {
    artModal.addEventListener('click', e => { if (e.target.id === 'artModal') closeModal(); });
}
const lightbox = $('lightbox');
if (lightbox) {
    lightbox.addEventListener('click', e => { if (e.target.id === 'lightbox') closeLightbox(); });
}

/* Lightbox for images inside article/project content */
document.addEventListener('click', function(e) {
    const img = e.target.closest('.detail-body img');
    if (img && img.src) {
        openLightbox(img.src, img.alt || '');
    }
});

/* Scroll effects */
window.addEventListener('scroll', () => {
    const navbar = $('navbar');
    if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 50);
    const scrollHint = $('scrollHint');
    if (scrollHint) scrollHint.classList.toggle('hide', window.scrollY > 200);
});

/* Keyboard shortcuts */
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        closeModal();
        closeLightbox();
    }
});

/* Load on DOM ready */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadContent);
} else {
    loadContent();
}
