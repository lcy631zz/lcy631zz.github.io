/* Main JS: language switcher, scroll, lightbox, content rendering */
let DATA=null, lang='zh-CN';

function loadContent(){
    try{
        DATA=window.I18N;
    }catch(e){
        console.error('Failed to load i18n data',e);
        return;
    }
    render();
}

function t(k){return DATA?.[lang]?.[k]??''}
function na(){return lang==='en'?'N/A':'无'}

function render(){
    if(!DATA)return;
    const d=DATA[lang];
    document.getElementById('siteName').textContent=d.site_name;
    document.getElementById('hBadge').textContent=d.hero.badge;
    document.getElementById('hT1').textContent=d.hero.title_1;
    document.getElementById('hTHL').textContent=d.hero.title_hl;
    document.getElementById('hT2').textContent=d.hero.title_2;
    document.getElementById('hT3').textContent=d.hero.title_3;
    document.getElementById('hTHL2').textContent=d.hero.title_hl2;
    document.getElementById('hT4').textContent=d.hero.title_4;
    document.getElementById('hSub').textContent=d.hero.subtitle;
    document.getElementById('hCta').textContent=d.hero.cta;
    document.getElementById('sHint').textContent=lang==='en'?'Scroll Down':'向下滚动';

    document.getElementById('aName').textContent=d.about.name;
    document.getElementById('aRole').textContent=d.about.role;
    document.getElementById('aIntroTitle').textContent=d.about.intro_title;
    document.getElementById('aIntro').textContent=d.about.intro_text;
    document.getElementById('aInfoTitle').textContent=d.about.info_title;
    document.getElementById('aInfo').textContent=d.about.info_text;

    document.getElementById('wDesc').textContent=d.articles.desc;
    document.getElementById('yDesc').textContent=d.yin.desc;
    document.getElementById('yQuote').textContent=d.yin.quote;
    document.getElementById('yQuoteA').textContent=d.yin.quote_author;
    document.getElementById('pDesc').textContent=d.projects.desc;
    document.getElementById('xDesc').textContent=d.xing.desc;
    document.getElementById('footer').textContent=d.footer;

    // Render article cards from Hugo data
    const ag=document.getElementById('artGrid');
    if(window.ARTICLES && window.ARTICLES.length){
        ag.innerHTML=window.ARTICLES.map((a,i)=>{
            const contentEsc = a.content ? a.content.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,"\\'") : '';
            return '<div class="article-card fi" onclick="openArticle('+i+')">'+
                '<div class="card-meta"><span class="card-tag">'+a.tag+'</span><span>'+a.date+'</span></div>'+
                '<h3>'+a.title+'</h3>'+
                '<p class="card-excerpt">'+(a.excerpt||'')+'</p>'+
                '<div class="card-footer"><span>'+(a.readTime||'')+'</span><span>'+(lang==='en'?'Read →':'阅读 →')+'</span></div>'+
                '</div>';
        }).join('');
        requestAnimationFrame(()=>ag.querySelectorAll('.fi').forEach(el=>el.classList.add('v')));
    }else{
        ag.innerHTML='<div class="empty"><div class="empty-icon">📝</div>'+na()+'</div>';
    }

    // Render yin grid from data
    const yg=document.getElementById('yinGrid');
    if(window.YIN && window.YIN.items && window.YIN.items.length){
        yg.innerHTML=window.YIN.items.map(y=>{
            const cap=(y.caption||'').replace(/'/g,"\\'");
            return '<div class="yin-item fi" onclick="openLightbox(\''+y.img+'\',\''+cap+'\')">'+
                '<img src="'+y.img+'" alt="'+(y.caption||'')+'" loading="lazy">'+
                (y.caption?'<div class="yin-caption">'+y.caption+'</div>':'')+
                '</div>';
        }).join('');
        requestAnimationFrame(()=>yg.querySelectorAll('.fi').forEach(el=>el.classList.add('v')));
    }else{
        yg.innerHTML='<div class="empty"><div class="empty-icon">🌿</div>'+na()+'</div>';
    }

    // Render project items from Hugo data
    const pl=document.getElementById('projList');
    if(window.PROJECTS && window.PROJECTS.length){
        pl.innerHTML=window.PROJECTS.map(p=>{
            const tags=(p.tags||[]).map(t=>'<span class="project-tag">'+t+'</span>').join('');
            return '<a href="'+(p.link||'#')+'" class="project-item fi">'+
                '<div class="project-icon">📁</div>'+
                '<div class="project-info"><h3>'+p.title+'</h3><p>'+(p.desc||'')+'</p></div>'+
                '<div class="project-tags">'+tags+'</div>'+
                '<span class="project-arrow">→</span>'+
                '</a>';
        }).join('');
        requestAnimationFrame(()=>pl.querySelectorAll('.fi').forEach(el=>el.classList.add('v')));
    }else{
        pl.innerHTML='<div class="empty">'+na()+'</div>';
    }

    // Render xing grid from data
    const xg=document.getElementById('xingGrid');
    if(window.XING && window.XING.items && window.XING.items.length){
        xg.innerHTML=window.XING.items.map(x=>{
            const cap=(x.caption||'').replace(/'/g,"\\'");
            return '<div class="xing-item fi" onclick="openLightbox(\''+x.img+'\',\''+cap+'\')">'+
                '<img src="'+x.img+'" alt="'+(x.caption||'')+'" loading="lazy">'+
                (x.place?'<div class="xing-place">'+x.place+'</div>':'')+
                (x.caption?'<div class="xing-caption">'+x.caption+'</div>':'')+
                '</div>';
        }).join('');
        requestAnimationFrame(()=>xg.querySelectorAll('.fi').forEach(el=>el.classList.add('v')));
    }else{
        xg.innerHTML='<div class="empty"><div class="empty-icon">✈️</div>'+na()+'</div>';
    }

    // Language switcher button states
    document.querySelectorAll('.lang-btn').forEach(b=>{
        b.classList.toggle('on', b.dataset.lang===lang);
    });
}

function setLang(l){
    lang=l;
    document.documentElement.lang=l;
    render();
}

function openArticle(i){
    const a=window.ARTICLES[i];
    if(!a)return;
    document.getElementById('mTitle').textContent=a.title;
    document.getElementById('mMeta').innerHTML='<span>'+(a.tag||'')+'</span><span>'+(a.date||'')+'</span><span>'+(a.readTime||'')+'</span>';
    document.getElementById('mBody').innerHTML=a.content||'<p>暂无内容</p>';
    document.getElementById('artModal').classList.add('show');
    document.body.style.overflow='hidden';
}
function closeModal(){document.getElementById('artModal').classList.remove('show');document.body.style.overflow=''}
document.getElementById('artModal').addEventListener('click',e=>{if(e.target.id==='artModal')closeModal()});

function openLightbox(src,cap){
    document.getElementById('lbImg').src=src;
    document.getElementById('lbCap').textContent=cap;
    document.getElementById('lightbox').classList.add('show');
    document.body.style.overflow='hidden';
}
function closeLightbox(){document.getElementById('lightbox').classList.remove('show');document.body.style.overflow=''}

window.addEventListener('scroll',()=>{
    document.getElementById('navbar').classList.toggle('scrolled',window.scrollY>50);
    document.getElementById('scrollHint').classList.toggle('hide',window.scrollY>200);
});

// Load on DOM ready
if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',loadContent)}else{loadContent()}
