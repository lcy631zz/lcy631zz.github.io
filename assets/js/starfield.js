/* Starfield canvas animation */
(function(){
    const cv=document.getElementById('cv');
    if(!cv)return; // No canvas on this page
    const cx=cv.getContext('2d'),P=[],F=[];
    let running=true;
    function rs(){cv.width=cv.parentElement.offsetWidth;cv.height=cv.parentElement.offsetHeight}
    rs();window.addEventListener('resize',rs);
    // Pause animation when not visible (mobile perf)
    if('IntersectionObserver' in window){
        new IntersectionObserver(entries=>{
            running=entries[0].isIntersecting;
        },{threshold:0}).observe(cv);
    }
    function R(a,b){return Math.random()*(b-a)+a}
    function rc(){const c=['#64B5F6','#81D4FA','#B39DDB','#CE93D8','#80DEEA','#FFF176','#FFAB91','#A5D6A7','#F48FB1'];return c[Math.floor(Math.random()*c.length)]}
    function d(x1,y1,x2,y2){return Math.sqrt((x2-x1)**2+(y2-y1)**2)}
    class S{constructor(){this.reset()}reset(){this.x=R(0,cv.width);this.y=R(0,cv.height);this.sz=R(.8,2.5);this.bs=this.sz;this.vx=R(-.3,.3);this.vy=R(-.3,.3);this.c=rc();this.o=R(.2,.8);this.ph=R(0,6.28);this.sp=R(.008,.025)}up(mx,my,ac){this.ph+=this.sp;this.o=.2+Math.abs(Math.sin(this.ph))*.6;if(ac){const dd=d(this.x,this.y,mx,my);if(dd<180){const f=(180-dd)/180,a=Math.atan2(my-this.y,mx-this.x);this.vx+=Math.cos(a)*f*.08;this.vy+=Math.sin(a)*f*.08;this.sz=this.bs+f*2}else this.sz=this.bs}else this.sz=this.bs;this.x+=this.vx;this.y+=this.vy;this.vx*=.995;this.vy*=.995;if(this.x<0)this.x=cv.width;if(this.x>cv.width)this.x=0;if(this.y<0)this.y=cv.height;if(this.y>cv.height)this.y=0}dr(){cx.save();cx.globalAlpha=this.o;cx.fillStyle=this.c;cx.shadowBlur=8;cx.shadowColor=this.c;cx.beginPath();cx.arc(this.x,this.y,this.sz,0,6.28);cx.fill();cx.restore()}}
    class P2{constructor(x,y,c){this.x=x;this.y=y;this.c=c;const a=R(0,6.28),s=R(2,7);this.vx=Math.cos(a)*s;this.vy=Math.sin(a)*s;this.sz=R(1.5,3.5);this.o=1;this.dc=R(.012,.028)}up(){this.vy+=.06;this.x+=this.vx;this.y+=this.vy;this.vx*=.98;this.vy*=.98;this.o-=this.dc;this.sz*=.97}dr(){cx.save();cx.globalAlpha=this.o;cx.fillStyle=this.c;cx.shadowBlur=12;cx.shadowColor=this.c;cx.beginPath();cx.arc(this.x,this.y,this.sz,0,6.28);cx.fill();cx.restore()}get dead(){return this.o<=0}}
    function init(){const n=Math.min(160,(cv.width*cv.height)/6000|0);P.length=0;for(let i=0;i<n;i++)P.push(new S)}
    let mx=0,my=0,ma=false;
    cv.addEventListener('mousemove',e=>{const r=cv.getBoundingClientRect();mx=e.clientX-r.left;my=e.clientY-r.top;ma=true});
    cv.addEventListener('mouseleave',()=>{ma=false});
    cv.addEventListener('click',e=>{const r=cv.getBoundingClientRect();const x=e.clientX-r.left,y=e.clientY-r.top,c=rc();for(let i=0;i<40;i++)F.push(new P2(x,y,c))});
    function ani(){if(running){cx.clearRect(0,0,cv.width,cv.height);P.forEach(p=>{p.up(mx,my,ma);p.dr()});F.forEach((f,i)=>{f.up();f.dr();if(f.dead)F.splice(i,1)})}requestAnimationFrame(ani)}
    init();ani();window.addEventListener('resize',init);
})();
