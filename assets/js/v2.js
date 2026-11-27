/* MIPL v2 — components + scroll choreography. Classic script, works from file://. */
(function(){
'use strict';
var d=document,html=d.documentElement,body=d.body,W=window;
var RM=W.matchMedia('(prefers-reduced-motion: reduce)').matches;
var FINE=W.matchMedia('(hover: hover) and (pointer: fine)').matches;
var DESK=function(){return W.innerWidth>900};
var R=html.getAttribute('data-root')||'';
var hasG=typeof W.gsap!=='undefined'&&typeof W.ScrollTrigger!=='undefined';
var lenis=null;
function $(s,c){return (c||d).querySelector(s)}
function $$(s,c){return Array.prototype.slice.call((c||d).querySelectorAll(s))}
function store(k,v){try{if(v===undefined)return sessionStorage.getItem(k);sessionStorage.setItem(k,v)}catch(e){return null}}
var ok={}; W.__mipl=ok;

/* ---------------- toast ---------------- */
var toastEl=$('.toast'),toastT;
function toast(msg,err){ if(!toastEl)return; $('p',toastEl).innerHTML=msg; toastEl.classList.toggle('err',!!err); $('.ic',toastEl).textContent=err?'!':'✓';
  toastEl.classList.add('show'); clearTimeout(toastT); toastT=setTimeout(function(){toastEl.classList.remove('show')},6000) }
if(toastEl) $('button',toastEl).addEventListener('click',function(){toastEl.classList.remove('show')});
W.miplToast=toast; ok.toast=!!toastEl;

/* ---------------- nav + menu ---------------- */
var nav=$('.nav'),lastY=0;
function navScroll(y){ if(!nav)return; nav.classList.toggle('scrolled',y>30); if(!body.classList.contains('menu-open')) nav.classList.toggle('hide',y>lastY+4&&y>400); if(y<lastY-4||y<400) nav.classList.remove('hide'); lastY=y }
var burger=$('.burger'),mm=$('.mmenu');
function setMenu(o){ body.classList.toggle('menu-open',o); burger.setAttribute('aria-expanded',o); mm.setAttribute('aria-hidden',!o); body.classList.toggle('lock',o); if(lenis)(o?lenis.stop():lenis.start()); if(o){var a=$('a',mm);setTimeout(function(){a&&a.focus()},50)} else burger.focus({preventScroll:true}) }
if(burger) burger.addEventListener('click',function(){setMenu(!body.classList.contains('menu-open'))});
d.addEventListener('keydown',function(e){ if(!body.classList.contains('menu-open'))return; if(e.key==='Escape')setMenu(false);
  if(e.key==='Tab'){var f=$$('a',mm).concat([burger]),i=f.indexOf(d.activeElement); if(e.shiftKey&&i<=0){e.preventDefault();f[f.length-1].focus()} else if(!e.shiftKey&&i===f.length-1){e.preventDefault();f[0].focus()}} });

/* ---------------- sticky CTA + back to top ---------------- */
var cta=$('.stickycta'),top=$('.totop'),ring=top&&$('circle',top),foot=$('.foot');
var C=2*Math.PI*24; if(ring){ring.style.strokeDasharray=C;ring.style.strokeDashoffset=C}
var hideZones=new Set(),lastCtaY=W.scrollY,ctaDirUp=false;
if(cta&&typeof IntersectionObserver!=='undefined'){
  var ctaObs=new IntersectionObserver(function(ents){
    ents.forEach(function(en){ if(en.isIntersecting) hideZones.add(en.target); else hideZones.delete(en.target) });
    uiScroll(W.scrollY);
  },{threshold:0.01});
  $$('#lineup,.ending,.explode,.band,form,.foot').forEach(function(el){ctaObs.observe(el)});
}
function uiScroll(y){
  var max=Math.max(1,d.documentElement.scrollHeight-innerHeight), p=y/max;
  if(top){ top.classList.toggle('show',y>600); if(ring) ring.style.strokeDashoffset=C*(1-p) }
  if(cta){
    if(y<lastCtaY-4) ctaDirUp=true;
    else if(y>lastCtaY+4) ctaDirUp=false;
    lastCtaY=y;
    var hide=hideZones.size>0||body.classList.contains('menu-open');
    cta.classList.toggle('hide',hide);
    cta.classList.toggle('show',!hide && ctaDirUp && y>innerHeight*0.9);
  }
  navScroll(y);
}
W.addEventListener('scroll',function(){uiScroll(W.scrollY)},{passive:true}); uiScroll(W.scrollY);
if(top) top.addEventListener('click',function(){ if(lenis) lenis.scrollTo(0,{duration:1.4}); else W.scrollTo({top:0,behavior:RM?'auto':'smooth'}); var m=$('#main'); m&&m.focus({preventScroll:true}) });
ok.cta=!!cta; ok.totop=!!top;

/* ---------------- page transitions (curtain) ---------------- */
var curtain=$('.curtain');
function internal(a){ var h=a.getAttribute('href'); if(!h||h.charAt(0)==='#'||a.target==='_blank'||a.hasAttribute('download'))return false;
  if(/^(mailto:|tel:|https?:|javascript:)/i.test(h))return false; return /\.html(\?|#|$)/.test(h) }
if(curtain && !RM && hasG){
  d.addEventListener('click',function(e){ var a=e.target.closest&&e.target.closest('a'); if(!a||e.defaultPrevented||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button!==0)return; if(!internal(a))return;
    var href=a.href; if(href.split('#')[0]===location.href.split('#')[0])return; e.preventDefault(); store('miplCurtain','1');
    gsap.set($$('i',curtain),{transformOrigin:'50% 100%'}); gsap.to($$('i',curtain),{scaleY:1,duration:.55,stagger:.06,ease:'power3.inOut',onComplete:function(){location.href=href}}) });
  if(html.classList.contains('arriving')){ gsap.fromTo($$('i',curtain),{scaleY:1,transformOrigin:'50% 0%'},{scaleY:0,duration:.7,stagger:.06,ease:'power3.inOut',delay:.05,onComplete:function(){html.classList.remove('arriving')}}) }
  W.addEventListener('pageshow',function(ev){ if(ev.persisted){ gsap.set($$('i',curtain),{scaleY:0}); html.classList.remove('arriving') } });
  ok.curtain=true;
} else { html.classList.remove('arriving') }

/* ---------------- lightbox ---------------- */
var lb=$('.lb');
if(lb){ var items=[],idx=0,last=null,img=$('img',lb),cap=$('.cap',lb),cnt=$('.cnt',lb);
  $$('[data-lb]').forEach(function(b,i){items.push({s:b.getAttribute('data-lb'),a:b.getAttribute('data-alt')||''}); b.setAttribute('data-cursor','View'); b.addEventListener('click',function(){open(i)})});
  function show(){var it=items[idx];img.src=it.s;img.alt=it.a;cap.textContent=it.a;cnt.textContent=(idx+1)+' / '+items.length}
  function open(i){idx=i;show();last=d.activeElement;lb.classList.add('open');lb.setAttribute('aria-hidden','false');$('.x',lb).focus();if(lenis)lenis.stop()}
  function close(){lb.classList.remove('open');lb.setAttribute('aria-hidden','true');if(lenis)lenis.start();last&&last.focus()}
  $('.x',lb).onclick=close; $('.pv',lb).onclick=function(){idx=(idx-1+items.length)%items.length;show()}; $('.nx',lb).onclick=function(){idx=(idx+1)%items.length;show()};
  lb.addEventListener('click',function(e){if(e.target===lb)close()});
  d.addEventListener('keydown',function(e){ if(!lb.classList.contains('open'))return; if(e.key==='Escape')close(); if(e.key==='ArrowLeft')$('.pv',lb).click(); if(e.key==='ArrowRight')$('.nx',lb).click();
    if(e.key==='Tab'){var f=$$('button',lb),i=f.indexOf(d.activeElement);e.preventDefault();f[(i+(e.shiftKey?-1:1)+f.length)%f.length].focus()} });
  ok.lightbox=items.length;
}

/* ---------------- tabs ---------------- */
$$('.tabs').forEach(function(t){ var tabs=$$('[role=tab]',t);
  function sel(i,focus){ tabs.forEach(function(b,j){ var on=i===j; b.setAttribute('aria-selected',on); b.tabIndex=on?0:-1; d.getElementById(b.getAttribute('aria-controls')).hidden=!on }); if(focus)tabs[i].focus() }
  tabs.forEach(function(b,i){ b.addEventListener('click',function(){sel(i)}); b.addEventListener('keydown',function(e){ var k=e.key,n=tabs.length;
    if(k==='ArrowRight'){e.preventDefault();sel((i+1)%n,1)} if(k==='ArrowLeft'){e.preventDefault();sel((i-1+n)%n,1)} if(k==='Home'){e.preventDefault();sel(0,1)} if(k==='End'){e.preventDefault();sel(n-1,1)} }) });
  ok.tabs=(ok.tabs||0)+1; });

/* ---------------- accordion (details, animated) ---------------- */
$$('.acc details').forEach(function(dt){ var s=$('summary',dt),b=$('.ac-body',dt);
  s.addEventListener('click',function(e){ if(RM||!hasG)return; e.preventDefault();
    if(dt.open){ gsap.to(b,{height:0,opacity:0,duration:.4,ease:'power2.inOut',onComplete:function(){dt.open=false;gsap.set(b,{clearProps:'all'})}}) }
    else { dt.open=true; gsap.from(b,{height:0,opacity:0,duration:.5,ease:'power3.out',clearProps:'all'}) } }); ok.accordion=(ok.accordion||0)+1 });

/* ---------------- before / after ---------------- */
$$('.ba').forEach(function(ba){ var r=$('input',ba); function u(){ba.style.setProperty('--pos',r.value+'%'); r.setAttribute('aria-valuetext',r.value+'% field photo')} r.addEventListener('input',u); u(); ok.beforeAfter=true });

/* ---------------- finder ---------------- */
var fin=$('#finder');
if(fin){ var cards=$$('.pcard',fin),cnt2=$('#fcount'),q=$('#fq'),empty=$('.fempty',fin),st={line:'all',sector:'all',q:''};
  var P=new URLSearchParams(location.search); if(P.get('sector'))st.sector=P.get('sector'); if(P.get('line'))st.line=P.get('line');
  function apply(){ var n=0; cards.forEach(function(c){ var m=(st.line==='all'||c.dataset.line===st.line)&&(st.sector==='all'||('|'+c.dataset.sectors+'|').indexOf('|'+st.sector+'|')>-1)&&(!st.q||c.dataset.text.indexOf(st.q)>-1); c.hidden=!m; if(m)n++ });
    cnt2.textContent=n+' of '+cards.length+' solutions'; empty.style.display=n?'none':'block';
    $$('[data-f]',fin).forEach(function(b){ b.setAttribute('aria-pressed', st[b.dataset.f]===b.dataset.v) });
    if(hasG&&!RM) gsap.fromTo(cards.filter(function(c){return !c.hidden}),{opacity:0,y:16},{opacity:1,y:0,duration:.45,stagger:.025,ease:'power2.out',overwrite:true});
    if(W.ScrollTrigger) ScrollTrigger.refresh(); }
  $$('[data-f]',fin).forEach(function(b){ b.addEventListener('click',function(){ st[b.dataset.f]=b.dataset.v; apply() }) });
  q.addEventListener('input',function(){ st.q=q.value.trim().toLowerCase(); apply() });
  $('#freset',fin).addEventListener('click',function(){ st={line:'all',sector:'all',q:''}; q.value=''; apply() });
  apply(); ok.finder=cards.length;
}

/* ---------------- contact form + toast ---------------- */
var form=$('#cform');
if(form){ var sel=$('#f-topic'),tp=new URLSearchParams(location.search).get('topic'); if(tp&&sel)$$('option',sel).forEach(function(o){if(o.value===tp)sel.value=tp});
  form.addEventListener('submit',function(e){ e.preventDefault(); var good=true;
    $$('[required]',form).forEach(function(el){ var f=el.closest('.field'),bad=!el.value.trim()||(el.type==='email'&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(el.value)); f.classList.toggle('bad',bad); el.setAttribute('aria-invalid',bad); if(bad&&good){el.focus();good=false} });
    if(!good){toast('Please fill in the highlighted fields.',true);return}
    if(form.company_website.value)return;
    var D={name:form.name.value,organisation:form.organisation.value,email:form.email.value,phone:form.phone.value,topic:sel.options[sel.selectedIndex].text,message:form.message.value};
    var ep=form.getAttribute('data-endpoint')||'', conf=ep&&ep.indexOf('YOUR_FORM_ID')<0&&location.protocol!=='file:';
    if(!conf){ var b='Name: '+D.name+'\nOrganisation: '+D.organisation+'\nEmail: '+D.email+'\nPhone: '+D.phone+'\nTopic: '+D.topic+'\n\n'+D.message;
      toast('Opening your email app with the message ready. Press send there, or write to <b>info@miplsolns.com</b>.');
      if(!W.__noMailto) setTimeout(function(){location.href='mailto:info@miplsolns.com?subject='+encodeURIComponent('Website enquiry: '+D.topic)+'&body='+encodeURIComponent(b)},300); ok.lastToast='mailto'; return }
    var btn=$('button[type=submit]',form); btn.disabled=true;
    fetch(ep,{method:'POST',headers:{'Accept':'application/json','Content-Type':'application/json'},body:JSON.stringify(D)})
     .then(function(r){if(!r.ok)throw 0;toast('Thank you, '+D.name.split(' ')[0]+'. Your message was sent.');form.reset()})
     .catch(function(){toast('Sending failed. Please email <b>info@miplsolns.com</b>.',true)}).then(function(){btn.disabled=false}) });
}
var mapBtn=$('#loadmap'); if(mapBtn) mapBtn.addEventListener('click',function(){var m=$('.map');m.innerHTML='<iframe title="Map: Maharshi Industries, Ahmedabad" loading="lazy" src="'+m.getAttribute('data-src')+'"></iframe>'});

/* ---------------- command-K search ---------------- */
var ck=$('.cmdk');
if(ck && W.MIPL_INDEX){ var inp=$('input',ck),ul=$('ul',ck),res=[],si=0,lastF=null;
  function render(){ var qv=inp.value.trim().toLowerCase(), words=qv.split(/\s+/).filter(Boolean);
    res=W.MIPL_INDEX.filter(function(x){ var h=(x.t+' '+x.k+' '+(x.s||'')).toLowerCase(); return words.every(function(w){return h.indexOf(w)>-1}) }).slice(0,qv?40:12);
    si=0; ul.innerHTML=res.length?res.map(function(x,i){return '<li role="option" id="ck-'+i+'" aria-selected="'+(i===0)+'"><a href="'+(/^(mailto|tel|https?):/.test(x.u)?x.u:R+x.u)+'" tabindex="-1"><span>'+x.t+'</span><small>'+x.k+'</small></a></li>'}).join(''):'<li class="empty">No results for "'+qv.replace(/</g,'')+'"</li>';
    inp.setAttribute('aria-activedescendant',res.length?'ck-0':'') }
  function mark(){ $$('li[role=option]',ul).forEach(function(li,i){li.setAttribute('aria-selected',i===si)}); var a=d.getElementById('ck-'+si); if(a){a.scrollIntoView({block:'nearest'});inp.setAttribute('aria-activedescendant','ck-'+si)} }
  function open(){ lastF=d.activeElement; ck.classList.add('open'); ck.setAttribute('aria-hidden','false'); inp.value=''; render(); setTimeout(function(){inp.focus()},20); if(lenis)lenis.stop(); ok.cmdkOpened=true }
  function close(){ ck.classList.remove('open'); ck.setAttribute('aria-hidden','true'); if(lenis)lenis.start(); lastF&&lastF.focus&&lastF.focus() }
  W.miplCmdk=open;
  d.addEventListener('keydown',function(e){ if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault(); ck.classList.contains('open')?close():open()}
    else if(e.key==='/'&&!/input|textarea|select/i.test(d.activeElement.tagName)&&!ck.classList.contains('open')){e.preventDefault();open()} });
  $$('[data-cmdk]').forEach(function(b){b.addEventListener('click',open)});
  inp.addEventListener('input',render);
  inp.addEventListener('keydown',function(e){ if(e.key==='ArrowDown'){e.preventDefault();si=Math.min(res.length-1,si+1);mark()} else if(e.key==='ArrowUp'){e.preventDefault();si=Math.max(0,si-1);mark()}
    else if(e.key==='Enter'){e.preventDefault(); var a=$('#ck-'+si+' a',ul); if(a){close();a.click()}} else if(e.key==='Escape'){close()} else if(e.key==='Tab'){e.preventDefault()} });
  ck.addEventListener('click',function(e){ if(e.target===ck)close(); var a=e.target.closest('a'); if(a){close()} });
  ok.cmdk=W.MIPL_INDEX.length;
}


$$('.ring img,.htl img,.explode img,.stack img').forEach(function(i){i.loading='eager'});
$$('.rc img').forEach(function(im){ im.addEventListener('error',function(){ if(im.dataset.fb)return; im.dataset.fb='1'; var p=im.parentNode,s=p&&p.querySelector('source'); if(s)s.remove(); im.src=im.getAttribute('src') }) });
/* ---------------- 3D CSS carousel ---------------- */
var r3=$('.ring3d');
if(r3){ var ringEl=$('.ring',r3),rcs=$$('.rc',r3),N=rcs.length,A=360/N,live=$('.ring-live'),idx3=0,rot={v:0},is3=false;
  function front(){ var i=((Math.round(-rot.v/A)%N)+N)%N; if(i!==idx3||!rcs[i].classList.contains('front')){idx3=i; rcs.forEach(function(c,j){c.classList.toggle('front',j===i); c.tabIndex=(!is3||j===i)?0:-1; c.setAttribute('aria-hidden',is3&&j!==i?'true':'false')}); if(live)live.textContent=(i+1)+' of '+N+': '+$('b',rcs[i]).textContent} }
  function apply(){ ringEl.style.transform='translateZ(-'+r3.__rz+'px) rotateY('+rot.v+'deg)'; front() }
  function go(dlt){ var tgt=(Math.round(rot.v/A)-dlt)*A; if(hasG&&!RM) gsap.to(rot,{v:tgt,duration:.8,ease:'power3.out',onUpdate:apply}); else {rot.v=tgt;apply()} }
  function setup(){ is3=DESK()&&!RM&&hasG; r3.classList.toggle('is3d',is3); if(is3){ var hh=Math.max(300,Math.min(520,innerHeight-260)), w=Math.round(hh*.7); r3.style.setProperty('--ch',hh+'px'); r3.style.setProperty('--cw',w+'px'); r3.__rz=Math.round(w/2/Math.tan(Math.PI/N))+70; rcs.forEach(function(c){c.style.setProperty('--rz',r3.__rz+'px')}); apply() } else { ringEl.style.transform=''; rcs.forEach(function(c){c.classList.remove('front');c.tabIndex=0;c.removeAttribute('aria-hidden')}) } ok.ring3d=is3?'3d':'flat' }
  setup(); W.addEventListener('resize',function(){clearTimeout(r3.__t);r3.__t=setTimeout(setup,200)});
  $$('[data-ring]').forEach(function(b){b.addEventListener('click',function(){ if(is3) go(+b.getAttribute('data-ring')); else ringEl.scrollBy({left:+b.getAttribute('data-ring')*300,behavior:'smooth'}) })});
  r3.addEventListener('keydown',function(e){ if(!is3)return; if(e.key==='ArrowRight'){e.preventDefault();go(1)} if(e.key==='ArrowLeft'){e.preventDefault();go(-1)} });
  var sx=null,sv=0,moved=false; r3.addEventListener('pointerdown',function(e){ if(!is3)return; sx=e.clientX; sv=rot.v; moved=false; r3.classList.add('drag') });
  W.addEventListener('pointermove',function(e){ if(sx===null)return; var dx=e.clientX-sx; if(Math.abs(dx)>4)moved=true; rot.v=sv+dx*.25; apply() });
  W.addEventListener('pointerup',function(){ if(sx===null)return; sx=null; r3.classList.remove('drag'); go(0) });
  r3.addEventListener('click',function(e){ if(moved){e.preventDefault();moved=false} },true);
  r3.__base=0;
}

/* ---------------- fine-pointer components ---------------- */
if(FINE && !RM){
  // custom cursor
  var cur=$('.cursor');
  if(cur && hasG){ body.classList.add('has-cursor'); var dot=$('.c-dot',cur),rg=$('.c-ring',cur),lab=$('span',cur);
    var dx=gsap.quickTo(dot,'x',{duration:.08}),dy=gsap.quickTo(dot,'y',{duration:.08}),rx=gsap.quickTo(rg,'x',{duration:.35,ease:'power3'}),ry=gsap.quickTo(rg,'y',{duration:.35,ease:'power3'});
    d.addEventListener('mousemove',function(e){dx(e.clientX);dy(e.clientY);rx(e.clientX);ry(e.clientY);cur.style.opacity=1},{passive:true});
    d.addEventListener('mouseleave',function(){cur.style.opacity=0});
    d.addEventListener('mousedown',function(){cur.classList.add('down')}); d.addEventListener('mouseup',function(){cur.classList.remove('down')});
    d.addEventListener('mouseover',function(e){ var t=e.target; var L=t.closest&&t.closest('[data-cursor]'), A=t.closest&&t.closest('a,button,summary,[role=tab],label,.ba'), T=t.closest&&t.closest('input:not([type=range]),textarea,select');
      cur.classList.toggle('label',!!L); lab.textContent=L?L.getAttribute('data-cursor'):''; cur.classList.toggle('hover',!L&&!!A&&!T); cur.classList.toggle('text',!!T) });
    ok.cursor=true; }
  // magnetic
  $$('.magnetic').forEach(function(el){ var lb2=$('.lbl',el)||el;
    el.addEventListener('mousemove',function(e){ var r=el.getBoundingClientRect(),x=e.clientX-r.left-r.width/2,y=e.clientY-r.top-r.height/2; gsap.to(el,{x:x*.35,y:y*.45,duration:.4,ease:'power3.out'}); gsap.to(lb2,{x:x*.15,y:y*.15,duration:.4}) });
    el.addEventListener('mouseleave',function(){ gsap.to([el,lb2],{x:0,y:0,duration:.9,ease:'elastic.out(1,.35)'}) }); ok.magnetic=(ok.magnetic||0)+1 });
  // tilt + spotlight cards
  $$('[data-tilt]').forEach(function(c){ c.addEventListener('mousemove',function(e){ var r=c.getBoundingClientRect(),px=(e.clientX-r.left)/r.width,py=(e.clientY-r.top)/r.height;
      c.style.setProperty('--mx',px*100+'%'); c.style.setProperty('--my',py*100+'%'); c.style.transform='perspective(900px) rotateX('+((.5-py)*6).toFixed(2)+'deg) rotateY('+((px-.5)*7).toFixed(2)+'deg) translateY(-4px)' });
    c.addEventListener('mouseleave',function(){c.style.transform=''}); ok.tilt=(ok.tilt||0)+1 });
  // logo wall spotlight
  $$('.lw').forEach(function(c){ c.addEventListener('mousemove',function(e){var r=c.getBoundingClientRect();c.style.setProperty('--mx',(e.clientX-r.left)+'px');c.style.setProperty('--my',(e.clientY-r.top)+'px')}) });
  // hover image reveal
  var hr=$('.hreveal');
  if(hr && hasG){ var hx=gsap.quickTo(hr,'x',{duration:.5,ease:'power3'}),hy=gsap.quickTo(hr,'y',{duration:.5,ease:'power3'}),cache={};
    $$('[data-reveal-img]').forEach(function(el){ el.addEventListener('mouseenter',function(e){ var s=el.getAttribute('data-reveal-img'); var im=cache[s]; if(!im){im=new Image();im.src=s;im.alt='';cache[s]=im}
        $$('img',hr).forEach(function(x){if(x!==im)x.remove()}); hr.appendChild(im); hr.classList.add('on'); hx(e.clientX); hy(e.clientY) });
      el.addEventListener('mousemove',function(e){hx(e.clientX);hy(e.clientY)}); el.addEventListener('mouseleave',function(){hr.classList.remove('on')}) }); ok.hoverReveal=true; }
}

/* ---------------- no GSAP fallback ---------------- */
function killIntro(){ var i=$('#intro'); if(i)i.remove(); body.classList.remove('lock'); var n=$('.nav .mlogo'); if(n)n.style.opacity=1; W.__introDone=true }
if(!hasG){ html.classList.add('no-intro'); killIntro(); W.__ready=true; return }
gsap.registerPlugin(ScrollTrigger);

if(!RM && typeof W.Lenis!=='undefined'){ lenis=new Lenis({lerp:.085}); lenis.on('scroll',function(e){ScrollTrigger.update();uiScroll(e.scroll)}); gsap.ticker.add(function(t){lenis.raf(t*1000)}); gsap.ticker.lagSmoothing(0); W.__lenis=lenis }
$$('a[href^="#"]').forEach(function(a){a.addEventListener('click',function(e){var t=a.getAttribute('href');if(t.length>1&&$(t)){e.preventDefault();lenis?lenis.scrollTo(t,{offset:-110}):$(t).scrollIntoView()}})});

/* ---------------- scroll choreography ---------------- */
function words(el){ if(el.__w)return $$('.w',el); el.__w=1; var out=''; el.childNodes.forEach(function(n){ if(n.nodeType===3) out+=n.textContent.split(/(\s+)/).map(function(w){return /^\s*$/.test(w)?w:'<span class="w">'+w+'</span>'}).join(''); else { n.classList&&n.classList.add('w'); out+=n.outerHTML } }); el.innerHTML=out; return $$('.w',el) }
function masked(el){ if(el.__m)return $$('.ln>span',el); el.__m=1; el.setAttribute('aria-label',el.textContent.replace(/\s+/g,' ').trim()); var out='';
  el.childNodes.forEach(function(n){ if(n.nodeType===3) out+=n.textContent.split(/(\s+)/).map(function(w){return /^\s*$/.test(w)?(w?' ':''):'<span class="ln" aria-hidden="true"><span>'+w+'</span></span>'}).join(''); else if(n.nodeName==='BR') out+='<br>'; else out+='<span class="ln" aria-hidden="true"><span>'+n.outerHTML+'</span></span>' });
  el.innerHTML=out; return $$('.ln>span',el) }
function themes(){ var secs=$$('section[data-theme]'); if(!secs.length)return; html.setAttribute('data-theme',secs[0].getAttribute('data-theme'));
  secs.forEach(function(s){ var ps=s.parentNode&&s.parentNode.classList.contains('pin-spacer')?s.parentNode:s; var st=s.getAttribute('data-theme')==='blue'?'top 35%':'top 55%'; ScrollTrigger.create({trigger:ps,start:st,end:'bottom 55%',onToggle:function(self){ if(self.isActive) html.setAttribute('data-theme',s.getAttribute('data-theme')) }}) }); ok.themes=secs.length }
function generic(){
  gsap.to('#prog',{scaleX:1,ease:'none',scrollTrigger:{start:0,end:'max',scrub:.3}}); ok.progress=true;
  $$('[data-split]').forEach(function(el){ gsap.from(masked(el),{yPercent:115,rotate:3,duration:1.1,stagger:.035,ease:'expo.out',scrollTrigger:{trigger:el,start:'top 88%'}}) });
  $$('[data-fill]').forEach(function(el){ gsap.to(words(el),{opacity:1,stagger:.12,ease:'none',scrollTrigger:{trigger:el,start:'top 82%',end:'bottom 45%',scrub:.6}}); ok.fill=true });
  $$('[data-up]').forEach(function(el){ gsap.from(el,{y:50,opacity:0,duration:1.1,ease:'expo.out',scrollTrigger:{trigger:el,start:'top 90%'}}) });
  $$('[data-stagger]').forEach(function(el){ gsap.from(el.children,{y:46,opacity:0,duration:1,stagger:.07,ease:'expo.out',scrollTrigger:{trigger:el,start:'top 88%'}}) });
  $$('[data-wipe]').forEach(function(el){ var im=$('img',el); if(!im||el.classList.contains('noimg'))return; var dir=el.getAttribute('data-wipe'); var from={left:'inset(0% 100% 0% 0% round 24px)',right:'inset(0% 0% 0% 100% round 24px)',up:'inset(100% 0% 0% 0% round 24px)',center:'inset(50% 50% 50% 50% round 24px)'}[dir||'left'];
    gsap.fromTo(el,{clipPath:from},{clipPath:'inset(0% 0% 0% 0% round 24px)',duration:.9,ease:'expo.inOut',immediateRender:true,scrollTrigger:{trigger:el,start:'top 92%'}});
    gsap.fromTo(im,{scale:1.3},{scale:1,duration:1.4,ease:'expo.out',scrollTrigger:{trigger:el,start:'top 92%'}}); ok.wipe=true });
  $$('[data-to]').forEach(function(el){ var o={v:+(el.dataset.from||0)}; gsap.to(o,{v:+el.dataset.to,duration:2,ease:'power3.out',scrollTrigger:{trigger:el,start:'top 90%'},onUpdate:function(){el.textContent=Math.round(o.v)},onComplete:function(){ok.counters=true}}) });
  // stacked cards
  var sc=$$('.scard'); sc.forEach(function(c,i){ if(i===sc.length-1)return; gsap.to(c,{scale:.9+i*.008,filter:'brightness(.9)',ease:'none',scrollTrigger:{trigger:sc[i+1],start:'top bottom',end:'top '+(90+(i+1)*14)+'px',scrub:true}}) }); if(sc.length)ok.stack=sc.length;
  // velocity marquee
  $$('.vtrack').forEach(function(tr){ var loop=gsap.to(tr,{xPercent:-50,ease:'none',duration:28,repeat:-1}); var sk=gsap.quickTo(tr,'skewX',{duration:.5,ease:'power3'}); var dir=1;
    ScrollTrigger.create({start:0,end:'max',onUpdate:function(self){ var v=self.getVelocity(); var s=gsap.utils.clamp(-14,14,v/-220); sk(s); if(self.direction!==dir){dir=self.direction; gsap.to(loop,{timeScale:dir,duration:.6})}
      gsap.to(loop,{timeScale:dir*(1+Math.min(4,Math.abs(v)/900)),duration:.3,overwrite:true,onComplete:function(){gsap.to(loop,{timeScale:dir,duration:1})}}); ok.vmarq=true }}) });
  // inner hero image subtle
  $$('[data-par] img').forEach(function(im){ gsap.fromTo(im,{yPercent:-5,scale:1.12},{yPercent:5,scale:1.12,ease:'none',scrollTrigger:{trigger:im.closest('[data-par]'),start:'top bottom',end:'bottom top',scrub:true}}) });
}
function desktop(){
  var mmq=gsap.matchMedia();
  mmq.add('(min-width: 901px)',function(){
    var hm=$('.hmask');
    if(hm){ var tl=gsap.timeline({scrollTrigger:{trigger:hm,start:'top top',end:'+=100%',scrub:1,pin:true}});
      tl.fromTo('.hmask .frame',{clipPath:'inset(0% 3% 22% 3% round 20px)'},{clipPath:'inset(0% 0% 0% 0% round 0px)',ease:'none'},0).fromTo('.hmask video',{scale:1.18},{scale:1,ease:'none'},0)
        .fromTo('.hmask .cap',{bottom:'calc(22% + 22px)'},{bottom:'40px',ease:'none'},0); ok.heroMask=true }
    var ex=$('.explode');
    if(ex){ ex.classList.add('ex-anim'); ScrollTrigger.refresh();
      var et=gsap.timeline({scrollTrigger:{trigger:ex,start:'top top',end:'+=220%',scrub:1,pin:true}});
      et.to('.ex-head',{opacity:0,y:-20,duration:.35,ease:'power2.in'},0)
        .to('.ex-half.l',{xPercent:-30,rotate:-3,filter:'brightness(.42)',ease:'power2.inOut',duration:1},0).to('.ex-half.r',{xPercent:30,rotate:3,filter:'brightness(.42)',ease:'power2.inOut',duration:1},0)
        .fromTo('.ex-core',{opacity:0,scale:.9},{opacity:1,scale:1,duration:.6},.35);
      $$('.ex-layer').forEach(function(l,i){ var sp=[[-1,-.6],[1,-.5],[1,.7]][i]||[0,0]; et.fromTo(l,{opacity:0,xPercent:-sp[0]*160,yPercent:-sp[1]*160,scale:.6,rotate:sp[0]*-8},{opacity:1,xPercent:0,yPercent:0,scale:1,rotate:sp[0]*2,duration:1,ease:'power3.out'},.25+i*.15) });
      $$('.ex-callout').forEach(function(c,i){ et.fromTo(c,{opacity:0,y:30},{opacity:1,y:0,duration:.5},.8+i*.15) });
      et.to({},{duration:.6}); ok.exploder=true;
      return function(){ ex.classList.remove('ex-anim') } }
  });
  mmq.add('(min-width: 901px)',function(){
    var h=$('.htl');
    if(h){ h.classList.add('pinned'); var tr=$('.htl-track',h);
      var tw=gsap.to(tr,{x:function(){return -(tr.scrollWidth-innerWidth+80)},ease:'none',scrollTrigger:{trigger:h,start:'top 120px',end:function(){return '+='+(tr.scrollWidth-innerWidth+80)},scrub:1,pin:true,invalidateOnRefresh:true}});
      gsap.to('.htl-line i',{scaleX:1,ease:'none',scrollTrigger:{trigger:h,start:'top 120px',end:function(){return '+='+(tr.scrollWidth-innerWidth+80)},scrub:1}});
      $$('.tl-node',h).forEach(function(n){ gsap.from(n,{opacity:.25,y:30,duration:.6,scrollTrigger:{trigger:n,containerAnimation:tw,start:'left 85%'}}) }); ok.timeline=true;
      return function(){ h.classList.remove('pinned') } }
  });
}

/* ---------------- intro (index) ---------------- */
function intro(done){
  var box=$('#intro'); if(!box){done();return}
  if(RM||html.classList.contains('arriving')){ killIntro(); done(); return }
  var I=$('#ilogo'),N=$('.nav .mlogo'),short=store('miplIntro')==='1';
  body.classList.add('lock'); if(lenis)lenis.stop(); gsap.set(N,{opacity:0});
  var heads=$$('.hero [data-hsplit]').map(function(h){h.__intro=1;return masked(h)}).reduce(function(a,b){return a.concat(b)},[]);
  gsap.set(heads,{yPercent:115}); gsap.set('.hero .fade-in',{opacity:0,y:16});
  var fin=false; function end(){ if(fin)return; fin=true; store('miplIntro','1'); gsap.set(N,{opacity:1}); box.remove(); body.classList.remove('lock'); if(lenis)lenis.start();
    gsap.to(heads,{yPercent:0,stagger:.05,duration:1.1,ease:'expo.out'}); gsap.to('.hero .fade-in',{opacity:1,y:0,duration:.8,stagger:.08,delay:.3});
    W.__introDone=true; done() }
  $('.stage',box).style.visibility='visible';
  var tl=gsap.timeline({delay:.15,onComplete:end});
  var sk=$('.skipintro',box); sk.addEventListener('click',function(){tl.progress(1)}); d.addEventListener('keydown',function k(e){if(e.key==='Escape'&&!fin){tl.progress(1);d.removeEventListener('keydown',k)}});
  if(short){ $('.stage',box).style.visibility='hidden'; tl.to('.door.l',{xPercent:-101,duration:.7,ease:'expo.inOut'},0).to('.door.r',{xPercent:101,duration:.7,ease:'expo.inOut'},0); return }
  var bp=$$('.bp',I); bp.forEach(function(p){var L=p.getTotalLength();p.style.strokeDasharray=L;p.style.strokeDashoffset=L});
  gsap.set($('.stem',I),{scaleY:0,transformOrigin:'50% 100%'}); gsap.set($('.dot',I),{y:-380,opacity:0}); gsap.set($('.bar',I),{scaleX:0,transformOrigin:'50% 50%'}); gsap.set($$('.tm',I),{opacity:0}); gsap.set('#wm span',{yPercent:115});
  tl.to(bp,{strokeDashoffset:0,duration:.9,ease:'power2.inOut'}).to(bp,{fillOpacity:1,strokeOpacity:0,duration:.35},.7)
    .to($('.stem',I),{scaleY:1,duration:.5,ease:'power3.out'},.6).to($('.dot',I),{y:0,opacity:1,duration:.65,ease:'bounce.out'},.9)
    .to($('.bar',I),{scaleX:1,duration:.4,ease:'expo.out'},1.1).to($$('.tm',I),{opacity:1,duration:.3},1.3).to('#wm span',{yPercent:0,stagger:.022,duration:.45,ease:'power3.out'},1.1)
    .addLabel('flip',2.0).to('#wm',{opacity:0,y:10,duration:.25},'flip').to($$('.tm',I),{opacity:0,duration:.2},'flip')
    .add(function(){var a=I.getBoundingClientRect(),b=N.getBoundingClientRect(); gsap.to(I,{x:(b.left+b.width/2)-(a.left+a.width/2),y:(b.top+b.height/2)-(a.top+a.height/2),scale:b.height/a.height,duration:.7,ease:'expo.inOut'})},'flip')
    .to('.door.l',{xPercent:-101,duration:.85,ease:'expo.inOut'},'flip+=.2').to('.door.r',{xPercent:101,duration:.85,ease:'expo.inOut'},'flip+=.2').to({},{duration:.05},'flip+=.8');
}
function innerHero(){ $$('[data-hsplit]').forEach(function(el){ if($('#intro')||el.__intro)return; gsap.from(masked(el),{yPercent:115,rotate:2,duration:1.1,stagger:.05,ease:'expo.out',delay:html.classList.contains('arriving')?.45:.1}) }); }

if(RM){ html.classList.add('no-intro'); killIntro(); gsap.set('#prog',{scaleX:0}); W.addEventListener('scroll',function(){var m=d.documentElement.scrollHeight-innerHeight;$('#prog').style.transform='scaleX('+(scrollY/m)+')'},{passive:true}); ok.progress=true; W.__ready=true; return }
intro(function(){ desktop(); themes(); generic(); innerHero(); if(d.fonts&&d.fonts.ready)d.fonts.ready.then(function(){ScrollTrigger.refresh()}); W.addEventListener('load',function(){ScrollTrigger.refresh()}); ScrollTrigger.refresh(); W.__ready=true });
})();
