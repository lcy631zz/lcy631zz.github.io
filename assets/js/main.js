/* Main JS: language switcher, scroll, lightbox, content rendering */
let DATA = null, lang = 'zh-CN';

/* Detect current page from URL */
function getPage() {
    const p = window.location.pathname.replace(/\/$/, '') || '/';
    if (p === '/') return 'home';
    if (p === '/about') return 'about';
    if (p === '/blog') return 'blog';
    if (p === '/projects') return 'projects';
    if (p === '/yin') return 'yin';
    if (p === '/xing') return 'xing';
    if (p.startsWith('/blog/')) return 'blog-single';
    if (p.startsWith('/projects/')) return 'project-single';
    return 'other';
}

function $(id) { return document.getElementById(id); }

function loadContent() {
    try {
        DATA = window.I18N;
    } catch (e) {
        console.error('Failed to load i18n data', e);
        return;
    }
    render();
}

function t(k) { return DATA?.[lang]?.[k] ?? ''; }
function na() { return lang === 'en' ? 'N/A' : '无'; }

function render() {
    if (!DATA) return;
    const d = DATA[lang];
    const page = getPage();

    /* Site name (all pages) */
    const sn = $('siteName');
    if (sn) sn.textContent = d.site_name;

    /* Homepage hero elements */
    if (page === 'home') {
        const map = {
            hBadge: d.hero.badge,
            hT1: d.hero.title_1,
            hTHL: d.hero.title_hl,
            hT2: d.hero.title_2,
            hT3: d.hero.title_3,
            hTHL2: d.hero.title_hl2,
            hT4: d.hero.title_4,
            hSub: d.hero.subtitle,
            sHint: lang === 'en' ? 'Scroll Down' : '向下探索',
            hubAboutTitle: d.about.name,
            hubAboutDesc: d.about.intro_text.split('\n')[0] || (lang === 'en' ? 'About Me' : '关于我'),
            hubArtTitle: d.articles.title,
            hubArtDesc: d.articles.hub_desc || d.articles.desc,
            hubProjTitle: d.projects.title,
            hubProjDesc: d.projects.hub_desc || d.projects.desc
        };
        for (const [id, val] of Object.entries(map)) {
            const el = $(id);
            if (el) el.textContent = val;
        }
        requestAnimationFrame(() => {
            document.querySelectorAll('#hero .fi').forEach(el => el.classList.add('v'));
        });
    }

    /* About page */
    if (page === 'about') {
        const a = d.about;
        const ids = { aName: a.name, aRole: a.role, aIntroTitle: a.intro_title, aIntro: a.intro_text, aInfoTitle: a.info_title, aInfo: a.info_text };
        for (const [id, val] of Object.entries(ids)) {
            const el = $(id);
            if (el) el.textContent = val;
        }
    }

    /* Yin section page */
    if (page === 'yin') {
        const pd = $('pageDesc');
        if (pd) pd.textContent = d.yin.desc;
        const yqt = $('yQuoteText'), yqa = $('yQuoteAuthor'), yq = $('yinQuote');
        if (yqt) yqt.textContent = d.yin.quote;
        if (yqa) yqa.textContent = d.yin.quote_author;
        if (yq && d.yin.quote) yq.style.display = 'block';
        renderYinGrid();
    }

    /* Xing section page */
    if (page === 'xing') {
        const pd = $('pageDesc');
        if (pd) pd.textContent = d.xing.desc;
        renderXingGrid();
    }

    /* Language switcher button states */
    document.querySelectorAll('.lang-btn').forEach(b => {
        b.classList.toggle('on', b.dataset.lang === lang);
    });

    /* Navigation active state */
    setNavActive(page);
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
        return '<div class="yin-item fi" onclick="openLightbox(\'' + y.img + '\',\'' + cap + '\')">' +
            '<img src="' + y.img + '" alt="' + (y.caption || '') + '" loading="lazy">' +
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
        return '<div class="xing-item fi" onclick="openLightbox(\'' + x.img + '\',\'' + cap + '\')">' +
            '<img src="' + x.img + '" alt="' + (x.caption || '') + '" loading="lazy">' +
            (x.place ? '<div class="xing-place">' + x.place + '</div>' : '') +
            (x.caption ? '<div class="xing-caption">' + x.caption + '</div>' : '') +
            '</div>';
    }).join('');
    requestAnimationFrame(() => {
        xg.querySelectorAll('.fi').forEach(el => el.classList.add('v'));
    });
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
        'blog-single': '/blog/',
        'project-single': '/projects/'
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
    render();
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
