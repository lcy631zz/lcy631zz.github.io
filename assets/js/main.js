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
    if (p === '/projects') return 'projects';
    if (p === '/bi') return 'bi';
    if (p.startsWith('/bi/')) return 'bi-single';
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
    const lbImg = $('lbImg'), lbCap = $('lbCap'), lbHint = $('lbHint'), lb = $('lightbox');
    if (lbImg) lbImg.src = img || '';
    if (lbCap) lbCap.textContent = cap || '';
    if (lb) lb.classList.add('show');
    document.body.style.overflow = 'hidden';

    // Show pinch-to-zoom hint on touch devices
    if (lbHint && ('ontouchstart' in window)) {
        lbHint.style.display = 'block';
        setTimeout(() => { lbHint.style.display = 'none'; }, 3200);
    }
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
        setText('hubAboutTitle', d.about?.name);
        setText('hubArtTitle', d.articles?.title);
        setText('hubArtDesc', d.articles?.hub_desc || d.articles?.desc);
        setText('hubProjTitle', d.projects?.title);
        setText('hubProjDesc', d.projects?.hub_desc || d.projects?.desc);
        setText('hubZhaiTitle', d.zhai?.title);
        setText('hubZhaiDesc', d.zhai?.hub_desc || d.zhai?.desc);
        setText('hubBiTitle', d.bi?.title);
        setText('hubBiDesc', d.bi?.hub_desc || d.bi?.desc);
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

    /* Bi section page */
    if (page === 'bi') {
        setText('pageDesc', d.bi?.desc);
    }

    /* S2T conversion for blog/bi single pages */
    if ((page === 'blog-single' || page === 'bi-single') && lang === 'zh-Hant') {
        const db = document.querySelector('.detail-body');
        if (db) {
            const walker = document.createTreeWalker(db, NodeFilter.SHOW_TEXT);
            const nodes = [];
            let n;
            while ((n = walker.nextNode())) nodes.push(n);
            nodes.forEach(node => {
                const t = node.textValue;
                if (t) node.textValue = s2tConvert(t);
            });
        }
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
            '<img src="' + src + '" alt="' + (y.caption || '') + '" loading="lazy" decoding="async">' +
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
            '<img src="' + src + '" alt="' + (x.caption || '') + '" loading="lazy" decoding="async">' +
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
            const maxLen = 120;
            const isLong = quote.length > maxLen;
            const displayQuote = isLong ? sqEscape(z.quote.substring(0, maxLen).trim()) + '…' : quote;
            html += '<div class="zhai-quote' + (isLong ? ' zhai-quote-truncated' : '') + '">"' + displayQuote + '"</div>' +
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
        'bi': '/bi/',
        'blog-single': '/blog/',
        'bi-single': '/bi/',
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
});

/* Keyboard shortcuts */
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        closeModal();
        closeLightbox();
    }
});

/* Hamburger menu toggle */
function toggleMenu() {
    const btn = $('hamburger');
    const links = $('navLinks');
    if (!btn || !links) return;
    btn.classList.toggle('active');
    links.classList.toggle('show');

    // Close menu when a link is clicked
    if (links.classList.contains('show')) {
        links.querySelectorAll('a').forEach(a => {
            a.addEventListener('click', function handler() {
                links.classList.remove('show');
                btn.classList.remove('active');
                links.querySelectorAll('a').forEach(l => l.removeEventListener('click', handler));
            });
        });
    }
}

/* S2T Converter */
const S2T_MAP = {};
function s2tInit() {
    S2T_MAP["万"] = "萬";
    S2T_MAP["与"] = "與";
    S2T_MAP["丑"] = "醜";
    S2T_MAP["专"] = "專";
    S2T_MAP["业"] = "業";
    S2T_MAP["丛"] = "叢";
    S2T_MAP["东"] = "東";
    S2T_MAP["丝"] = "絲";
    S2T_MAP["丢"] = "丟";
    S2T_MAP["两"] = "兩";
    S2T_MAP["严"] = "嚴";
    S2T_MAP["丧"] = "喪";
    S2T_MAP["个"] = "個";
    S2T_MAP["丰"] = "豐";
    S2T_MAP["临"] = "臨";
    S2T_MAP["为"] = "為";
    S2T_MAP["丽"] = "麗";
    S2T_MAP["举"] = "舉";
    S2T_MAP["么"] = "麼";
    S2T_MAP["义"] = "義";
    S2T_MAP["乌"] = "烏";
    S2T_MAP["乐"] = "樂";
    S2T_MAP["乔"] = "喬";
    S2T_MAP["习"] = "習";
    S2T_MAP["乡"] = "鄉";
    S2T_MAP["书"] = "書";
    S2T_MAP["买"] = "買";
    S2T_MAP["乱"] = "亂";
    S2T_MAP["争"] = "爭";
    S2T_MAP["于"] = "於";
    S2T_MAP["亏"] = "虧";
    S2T_MAP["云"] = "雲";
    S2T_MAP["亚"] = "亞";
    S2T_MAP["产"] = "產";
    S2T_MAP["亩"] = "畝";
    S2T_MAP["亲"] = "親";
    S2T_MAP["亵"] = "褻";
    S2T_MAP["亿"] = "億";
    S2T_MAP["仅"] = "僅";
    S2T_MAP["从"] = "從";
    S2T_MAP["仑"] = "侖";
    S2T_MAP["仓"] = "倉";
    S2T_MAP["仪"] = "儀";
    S2T_MAP["们"] = "們";
    S2T_MAP["价"] = "價";
    S2T_MAP["众"] = "眾";
    S2T_MAP["优"] = "優";
    S2T_MAP["伙"] = "夥";
    S2T_MAP["会"] = "會";
    S2T_MAP["伛"] = "傴";
    S2T_MAP["伞"] = "傘";
    S2T_MAP["伟"] = "偉";
    S2T_MAP["传"] = "傳";
    S2T_MAP["伤"] = "傷";
    S2T_MAP["伥"] = "倀";
    S2T_MAP["伦"] = "倫";
    S2T_MAP["伧"] = "傖";
    S2T_MAP["伪"] = "偽";
    S2T_MAP["伫"] = "佇";
    S2T_MAP["体"] = "體";
    S2T_MAP["余"] = "餘";
    S2T_MAP["佣"] = "傭";
    S2T_MAP["佥"] = "僉";
    S2T_MAP["侠"] = "俠";
    S2T_MAP["侣"] = "侶";
    S2T_MAP["侥"] = "僥";
    S2T_MAP["侦"] = "偵";
    S2T_MAP["侧"] = "側";
    S2T_MAP["侨"] = "僑";
    S2T_MAP["侩"] = "儈";
    S2T_MAP["侪"] = "儕";
    S2T_MAP["侬"] = "儂";
    S2T_MAP["俣"] = "俁";
    S2T_MAP["俦"] = "儔";
    S2T_MAP["俨"] = "儼";
    S2T_MAP["俩"] = "倆";
    S2T_MAP["俪"] = "儷";
    S2T_MAP["俭"] = "儉";
    S2T_MAP["债"] = "債";
    S2T_MAP["倾"] = "傾";
    S2T_MAP["偬"] = "傯";
    S2T_MAP["偻"] = "僂";
    S2T_MAP["偾"] = "僨";
    S2T_MAP["偿"] = "償";
    S2T_MAP["傥"] = "儻";
    S2T_MAP["傧"] = "儐";
    S2T_MAP["储"] = "儲";
    S2T_MAP["傩"] = "儺";
    S2T_MAP["僵"] = "殭";
    S2T_MAP["儿"] = "兒";
    S2T_MAP["兖"] = "兗";
    S2T_MAP["党"] = "黨";
    S2T_MAP["兰"] = "蘭";
    S2T_MAP["关"] = "關";
    S2T_MAP["兴"] = "興";
    S2T_MAP["兹"] = "茲";
    S2T_MAP["养"] = "養";
    S2T_MAP["兽"] = "獸";
    S2T_MAP["内"] = "內";
    S2T_MAP["册"] = "冊";
    S2T_MAP["写"] = "寫";
    S2T_MAP["军"] = "軍";
    S2T_MAP["农"] = "農";
    S2T_MAP["冯"] = "馮";
    S2T_MAP["冲"] = "沖";
    S2T_MAP["决"] = "決";
    S2T_MAP["况"] = "況";
    S2T_MAP["冻"] = "凍";
    S2T_MAP["净"] = "淨";
    S2T_MAP["凄"] = "淒";
    S2T_MAP["准"] = "準";
    S2T_MAP["凉"] = "涼";
    S2T_MAP["减"] = "減";
    S2T_MAP["凑"] = "湊";
    S2T_MAP["几"] = "幾";
    S2T_MAP["凤"] = "鳳";
    S2T_MAP["凫"] = "鳧";
    S2T_MAP["凭"] = "憑";
    S2T_MAP["凯"] = "凱";
    S2T_MAP["凶"] = "兇";
    S2T_MAP["击"] = "擊";
    S2T_MAP["凿"] = "鑿";
    S2T_MAP["刍"] = "芻";
    S2T_MAP["划"] = "劃";
    S2T_MAP["刘"] = "劉";
    S2T_MAP["则"] = "則";
    S2T_MAP["刚"] = "剛";
    S2T_MAP["创"] = "創";
    S2T_MAP["删"] = "刪";
    S2T_MAP["刨"] = "鉋";
    S2T_MAP["别"] = "別";
    S2T_MAP["刭"] = "剄";
    S2T_MAP["刹"] = "剎";
    S2T_MAP["刾"] = "剾";
    S2T_MAP["刿"] = "劌";
    S2T_MAP["剀"] = "剴";
    S2T_MAP["剂"] = "劑";
    S2T_MAP["剉"] = "銼";
    S2T_MAP["剐"] = "剮";
    S2T_MAP["剑"] = "劍";
    S2T_MAP["剥"] = "剝";
    S2T_MAP["剣"] = "劍";
    S2T_MAP["剤"] = "劑";
    S2T_MAP["剧"] = "劇";
    S2T_MAP["剱"] = "劔";
    S2T_MAP["剿"] = "勦";
    S2T_MAP["刽"] = "劊";
    S2T_MAP["刾"] = "劎";
    S2T_MAP["劝"] = "勸";
    S2T_MAP["办"] = "辦";
    S2T_MAP["务"] = "務";
    S2T_MAP["劢"] = "勱";
    S2T_MAP["动"] = "動";
    S2T_MAP["劭"] = "勛";
    S2T_MAP["势"] = "勢";
    S2T_MAP["勋"] = "勛";
    S2T_MAP["勐"] = "猛";
    S2T_MAP["勚"] = "勩";
    S2T_MAP["勧"] = "勸";
    S2T_MAP["勲"] = "勳";
    S2T_MAP["匀"] = "勻";
    S2T_MAP["匮"] = "匱";
    S2T_MAP["区"] = "區";
    S2T_MAP["医"] = "醫";
    S2T_MAP["华"] = "華";
    S2T_MAP["协"] = "協";
    S2T_MAP["单"] = "單";
    S2T_MAP["卖"] = "賣";
    S2T_MAP["卢"] = "盧";
    S2T_MAP["卤"] = "鹵";
    S2T_MAP["卫"] = "衛";
    S2T_MAP["却"] = "卻";
    S2T_MAP["厅"] = "廳";
    S2T_MAP["历"] = "曆";
    S2T_MAP["厉"] = "厲";
    S2T_MAP["压"] = "壓";
    S2T_MAP["厌"] = "厭";
    S2T_MAP["厍"] = "厙";
    S2T_MAP["厐"] = "厖";
    S2T_MAP["厕"] = "廁";
    S2T_MAP["厘"] = "釐";
    S2T_MAP["厠"] = "廁";
    S2T_MAP["厢"] = "廂";
    S2T_MAP["厣"] = "厴";
    S2T_MAP["厦"] = "廈";
    S2T_MAP["厨"] = "廚";
    S2T_MAP["厩"] = "廄";
    S2T_MAP["厮"] = "廝";
    S2T_MAP["厯"] = "曆";
    S2T_MAP["厰"] = "廠";
    S2T_MAP["县"] = "縣";
    S2T_MAP["叁"] = "參";
    S2T_MAP["参"] = "參";
    S2T_MAP["叆"] = "靉";
    S2T_MAP["叇"] = "靆";
    S2T_MAP["双"] = "雙";
    S2T_MAP["发"] = "發";
    S2T_MAP["变"] = "變";
    S2T_MAP["叙"] = "敘";
    S2T_MAP["叠"] = "疊";
    S2T_MAP["台"] = "臺";
    S2T_MAP["叶"] = "葉";
    S2T_MAP["号"] = "號";
    S2T_MAP["叹"] = "嘆";
    S2T_MAP["叽"] = "嘰";
    S2T_MAP["吁"] = "籲";
    S2T_MAP["吊"] = "弔";
    S2T_MAP["后"] = "後";
    S2T_MAP["吓"] = "嚇";
    S2T_MAP["吨"] = "噸";
    S2T_MAP["听"] = "聽";
    S2T_MAP["启"] = "啟";
    S2T_MAP["吴"] = "吳";
    S2T_MAP["呉"] = "吳";
    S2T_MAP["呐"] = "吶";
    S2T_MAP["呒"] = "嘸";
    S2T_MAP["呓"] = "囈";
    S2T_MAP["呕"] = "嘔";
    S2T_MAP["呖"] = "嚦";
    S2T_MAP["员"] = "員";
    S2T_MAP["呙"] = "咼";
    S2T_MAP["呛"] = "嗆";
    S2T_MAP["呜"] = "嗚";
    S2T_MAP["咙"] = "嚨";
    S2T_MAP["咛"] = "嚀";
    S2T_MAP["咝"] = "噝";
    S2T_MAP["咤"] = "吒";
    S2T_MAP["呗"] = "唄";
    S2T_MAP["响"] = "響";
    S2T_MAP["哑"] = "啞";
    S2T_MAP["哒"] = "噠";
    S2T_MAP["哓"] = "嘵";
    S2T_MAP["哔"] = "嗶";
    S2T_MAP["哕"] = "噦";
    S2T_MAP["哗"] = "嘩";
    S2T_MAP["哙"] = "噲";
    S2T_MAP["哜"] = "嚌";
    S2T_MAP["哝"] = "噥";
    S2T_MAP["哟"] = "喲";
    S2T_MAP["唇"] = "脣";
    S2T_MAP["唖"] = "啞";
    S2T_MAP["唚"] = "唫";
    S2T_MAP["唛"] = "嘜";
    S2T_MAP["唝"] = "嗊";
    S2T_MAP["唠"] = "嘮";
    S2T_MAP["唡"] = "啢";
    S2T_MAP["唢"] = "嗩";
    S2T_MAP["唤"] = "喚";
    S2T_MAP["啧"] = "嘖";
    S2T_MAP["啬"] = "嗇";
    S2T_MAP["啭"] = "囀";
    S2T_MAP["啮"] = "齧";
    S2T_MAP["啰"] = "囉";
    S2T_MAP["啴"] = "嘽";
    S2T_MAP["喱"] = "嚨";
    S2T_MAP["営"] = "營";
    S2T_MAP["喷"] = "噴";
    S2T_MAP["喽"] = "嘍";
    S2T_MAP["喾"] = "嚳";
    S2T_MAP["嗫"] = "囁";
    S2T_MAP["嗳"] = "噯";
    S2T_MAP["嘘"] = "噓";
    S2T_MAP["嘠"] = "嘰";
    S2T_MAP["嘤"] = "嚶";
    S2T_MAP["嘨"] = "嘯";
    S2T_MAP["嘱"] = "囑";
    S2T_MAP["噜"] = "嚕";
    S2T_MAP["咸"] = "鹹";
}
function s2tConvert(text) {
    if (!text) return text;
    return text.split("").map(c => S2T_MAP[c] || c).join("");
}
s2tInit();

/* Load on DOM ready */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadContent);
} else {
    loadContent();
}
