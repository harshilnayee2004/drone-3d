import json, os, re, sys, base64
sys.path.insert(0,'/workspace/mipl-v2-src')
from data import *
OUT='/workspace/MIPL-website-v2'
SRC='/workspace/mipl-v2-src'
# ---- assets: css with fonts, js ----
css=open(SRC+'/v2.css').read()
for k,f in [('FONT_geistmono','geistmono'),('FONT_geist','geist'),('FONT_iserifi','iserif-i'),('FONT_iserif','iserif')]:
    css=css.replace(k,'data:font/woff2;base64,'+base64.b64encode(open(f'{SRC}/fonts/{f}.woff2','rb').read()).decode())
open(OUT+'/assets/css/v2.css','w').write(css)
for f in ['v2.js','v2-3d.js']:
    if os.path.exists(f'{SRC}/{f}'): open(f'{OUT}/assets/js/{f}','w').write(open(f'{SRC}/{f}').read())

# ---- sector tagging from text ----
SECT=[('Defence',r'defen[cs]e|army|military|navy|naval|air force|forces|combat|battle|eod|ied|bomb|lac posts|ammunition|paramilitary'),
 ('Nuclear',r'nuclear|radiation|radioactive|atomic|reactor|hot cell|barc|nfc|zircalloy|phwr'),
 ('Railways',r'rail|loco|metro'),('Oil & Gas',r'oil|gas|pipeline|refiner|vessel'),
 ('Public Safety',r'fire|rescue|police|law enforcement|disaster|first responder|emergency|ats|nsg|ndrf|bomb disposal'),
 ('Education',r'education|college|engineering and medical'),('Transportation',r'driver|vehicle|bus |road'),
 ('Infrastructure',r'bridge|dam|infrastructure|port|offshore|storage tank'),('Supply Chain / Logistics',r'supply chain|warehouse|logistic|inventory'),
 ('Industry',r'pharma|dairy|power plant|manufactur|mining|industrial')]
def tags(p,L):
    txt=(p['name']+' '+p.get('description','')+' '+' '.join(p.get('useCases',[]) or [])+' '+' '.join((f.get('title','')+' '+f.get('text','')) for f in (p.get('features') or [])+(p.get('industries') or []))).lower()
    t=[s for s,rx in SECT if re.search(rx,txt)]
    return t or [s if s in dict(SECT) else s for s in L['sectors']]
ALLP=[]
for L in LINES:
    for p in L['products']:
        imgs=[u for u in (p.get('images') or [])+(p.get('media') or []) if u and has(u)]
        ALLP.append(dict(p=p,L=L,img=imgs[0] if imgs else L['hero'],tags=tags(p,L)))
SECTORS=[s for s,_ in SECT if any(s in x['tags'] for x in ALLP)]
LN=lambda L: L['title'].split(' —')[0]

# ---- search index ----
IDX=[dict(t='Home',u='index.html',k='Page'),dict(t='Products & finder',u='products.html',k='Page'),dict(t='About MIPL',u='about.html',k='Page',s='company vision mission history S.S.B.I'),
 dict(t='Clients & deliveries',u='clients.html',k='Page',s='DRDO BARC Navy Army Railways events'),dict(t='Careers',u='careers.html',k='Page',s='jobs work cv'),dict(t='Contact',u='contact.html',k='Page',s='email phone address enquiry')]
IDX+=[dict(t=LN(L),u=f'products/{L["slug"]}.html',k='Product line',s=L['summary']) for L in LINES]
IDX+=[dict(t=x['p']['name'],u=f'products/{x["L"]["slug"]}.html#{x["p"]["id"]}',k=LN(x['L']),s=' '.join(x['tags'])+' '+x['p'].get('description','')[:160]) for x in ALLP]
IDX+=[dict(t=f'{s} solutions',u=f'products.html?sector={s}',k='Sector') for s in SECTORS]
IDX+=[dict(t=CT['email'],u='mailto:'+CT['email'],k='Email'),dict(t=CT['mobile'],u='tel:+919727388634',k='Phone')]
open(OUT+'/assets/js/search-index.js','w').write('window.MIPL_INDEX='+json.dumps(IDX,ensure_ascii=False)+';')

# ---- chrome ----
NAVL=[('products.html','Products'),('about.html','About'),('clients.html','Clients'),('careers.html','Careers')]
def head(title,desc,R,path,theme):
    ld={"@context":"https://schema.org","@type":"Organization","name":CO['name'],"alternateName":"MIPL","url":DOMAIN,"logo":DOMAIN+"assets/logo/mipl-logo.svg","email":CT['email'],"telephone":"+91 97273 88634","foundingDate":"2014",
        "address":{"@type":"PostalAddress","streetAddress":"505-509, 5th Floor, Aarya Epoch, Navrangpura","addressLocality":"Ahmedabad","addressRegion":"Gujarat","postalCode":"380009","addressCountry":"IN"},"sameAs":[CT['linkedin']]}
    return f'''<!doctype html>
<html lang="en" data-root="{R}" data-theme="{theme}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{DOMAIN}{path}">
<meta name="theme-color" content="#ECEAE4">
<meta property="og:type" content="website"><meta property="og:site_name" content="Maharshi Industries Pvt. Ltd."><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{DOMAIN}{path}"><meta property="og:image" content="{DOMAIN}assets/og/og-default.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{DOMAIN}assets/og/og-default.jpg">
<link rel="icon" href="{R}favicon.ico" sizes="48x48"><link rel="icon" href="{R}favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="{R}apple-touch-icon.png"><link rel="manifest" href="{R}site.webmanifest">
<link rel="stylesheet" href="{R}assets/css/v2.css">
<script>(function(h){{h.classList.add('js');try{{if(sessionStorage.getItem('miplCurtain')==='1'){{sessionStorage.removeItem('miplCurtain');if(!matchMedia('(prefers-reduced-motion: reduce)').matches)h.classList.add('arriving')}}}}catch(e){{}}setTimeout(function(){{h.classList.remove('arriving')}},2500)}})(document.documentElement);</script>
<script type="application/ld+json">{json.dumps(ld)}</script></head>'''
def nav(R,cur):
    li=''.join(f'<li><a href="{R}{h}"{" aria-current=page" if cur==h else ""}>{t}</a></li>' for h,t in NAVL)
    sub=''.join(f'<li><a href="{R}products/{L["slug"]}.html">{e(L["short"])}</a></li>' for L in LINES)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="nav"><a class="brand" href="{R}index.html" aria-label="Maharshi Industries, home">{logo_svg(hidden=True)}<b>MIPL</b></a>
<nav aria-label="Main"><ul>{li}</ul></nav>
<div class="nright"><button class="kbtn" type="button" data-cmdk aria-label="Search the site (Ctrl+K)"><span aria-hidden="true">⌕</span><span class="t">Search</span><kbd aria-hidden="true">Ctrl K</kbd></button>
<a class="btn solid navcta magnetic" href="{R}contact.html"><span class="lbl">Contact</span> <span class="ar">↗</span></a>
<button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="mmenu"><span></span><span></span></button></div></header>
<div class="mmenu" id="mmenu" aria-hidden="true"><nav aria-label="Mobile"><ul><li><a href="{R}index.html">Home</a></li><li><a href="{R}products.html">Products</a><ul class="sub">{sub}</ul></li><li><a href="{R}about.html">About</a></li><li><a href="{R}clients.html">Clients</a></li><li><a href="{R}careers.html">Careers</a></li><li><a href="{R}contact.html">Contact</a></li></ul></nav><p class="mono" style="color:#a9a8a3">{e(CT["email"])} · {e(CT["mobile"])}</p></div>'''
def footer(R):
    pl=''.join(f'<li><a href="{R}products/{L["slug"]}.html">{e(LN(L))}</a></li>' for L in LINES)
    return f'''<footer class="foot" data-theme-foot><div class="wrap"><div class="fgrid">
<div class="fbrand">{logo_svg(label="Maharshi Industries logo")}<p><b style="color:var(--fg)">Maharshi Industries Pvt. Ltd.</b><br>{e(CO["motto"])}. Part of the {e(CO["group"])}, Ahmedabad, since 2014.</p><img class="mii" src="{R}assets/img/make-india-logo.png" alt="Make in India" width="74" height="34" loading="lazy"></div>
<div><p class="mono">Products</p><ul>{pl}</ul></div>
<div><p class="mono">Company</p><ul><li><a href="{R}about.html">About</a></li><li><a href="{R}clients.html">Clients &amp; deliveries</a></li><li><a href="{R}careers.html">Careers</a></li><li><a href="{R}contact.html">Contact</a></li><li><a href="{e(CT["linkedin"])}" target="_blank" rel="noopener">LinkedIn ↗</a></li></ul></div>
<div><p class="mono">Visit</p><ul><li style="font-size:15px">{e(CT["address"])}</li><li><a href="mailto:{CT["email"]}">{CT["email"]}</a></li><li><a href="tel:+919727388634">{CT["mobile"]}</a></li><li class="mut" style="font-size:14px">{e(CT["hours"])}</li></ul></div></div>
<div class="fbot"><p class="mono">© {YEAR} Maharshi Industries Pvt. Ltd.</p><p class="mono">Press <kbd>Ctrl K</kbd> to search · Navnirmit Bharat</p></div></div></footer>'''
def chrome(R,sticky=True):
    return (f'''<div class="lb" role="dialog" aria-modal="true" aria-label="Image viewer" aria-hidden="true"><img alt=""><p class="cnt mono"></p><button class="x" aria-label="Close">✕</button><button class="pv" aria-label="Previous image">←</button><button class="nx" aria-label="Next image">→</button><p class="cap mono"></p></div>
<div class="cmdk" role="dialog" aria-modal="true" aria-label="Quick search" aria-hidden="true"><div class="box"><input type="text" role="combobox" aria-expanded="true" aria-controls="ck-list" aria-autocomplete="list" placeholder="Search products, pages, sectors…" aria-label="Search"><ul id="ck-list" role="listbox"></ul><div class="foot"><span>↑↓ move</span><span>↵ open</span><span>esc close</span></div></div></div>
<div class="toast" role="status" aria-live="polite"><span class="ic" aria-hidden="true">✓</span><p></p><button type="button" aria-label="Dismiss">✕</button></div>
<button class="totop" type="button" aria-label="Back to top"><svg viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="24"/></svg><span aria-hidden="true">↑</span></button>
{f'<div class="stickycta"><p>Have a requirement?</p><a class="btn" href="{R}contact.html">Talk to MIPL <span class="ar">→</span></a></div>' if sticky else ''}
<div class="cursor" aria-hidden="true"><div class="c-ring"><span></span></div><div class="c-dot"></div></div>
<div class="hreveal" aria-hidden="true"></div>
<div class="curtain" aria-hidden="true"><i></i><i></i><i></i><i></i></div>''')
def scripts(R,three=False):
    s=f'<script src="{R}assets/vendor/gsap.min.js"></script><script src="{R}assets/vendor/ScrollTrigger.min.js"></script><script src="{R}assets/vendor/lenis.min.js"></script><script src="{R}assets/js/search-index.js"></script><script src="{R}assets/js/v2.js"></script>'
    if three: s+=f'<script src="{R}assets/js/v2-3d.js" data-vendor="{R}assets/vendor/"></script>'
    return s
def page(fn,title,desc,body,R='',cur='',theme='light',extra='',sticky=True,three=False):
    path=fn if fn!='index.html' else ''
    doc=head(title,desc,R,path,theme)+f'\n<body>\n<div id="prog" aria-hidden="true"></div><div class="grid-lines" aria-hidden="true"><i></i><i></i><i></i><i></i></div>{extra}{nav(R,cur)}\n<main id="main" tabindex="-1">{body}</main>\n{footer(R)}\n{chrome(R,sticky)}\n{scripts(R,three)}\n</body></html>'
    p=os.path.join(OUT,fn); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w').write(doc)
def band(R,label,title,href,btn):
    return f'<div class="band" data-up><div><p class="mono">{label}</p><h2 class="h-m" style="margin-top:14px;max-width:820px">{title}</h2></div><a class="btn solid magnetic" href="{href}"><span class="lbl">{btn}</span> <span class="ar">→</span></a></div>'
def pcard(x,R):
    p,L=x['p'],x['L']
    txt=(p['name']+' '+LN(L)+' '+' '.join(x['tags'])+' '+p.get('description','')).lower()
    return (f'<a class="pcard" data-tilt href="{R}products/{L["slug"]}.html#{p["id"]}" data-line="{L["slug"]}" data-sectors="{e("|".join(x["tags"]))}" data-text="{e(txt)}">'
            f'<div class="ph" data-cursor="Open">{pic(x["img"],p["name"],R,sizes="(max-width:560px) 100vw, (max-width:1100px) 50vw, 30vw")}</div><div class="tx"><span class="mono">{e(LN(L))}</span><h3>{e(p["name"])}</h3>'
            f'<p>{e(first(p.get("description","")))}</p><div class="ft"><span class="chips">{"".join(f"<span class=chip>{e(t)}</span>" for t in x["tags"][:2])}</span><span aria-hidden="true">↗</span></div></div></a>')
def htl(R):
    nodes=[dict(y='2014',t=f'Maharshi Industries is founded in Ahmedabad as part of the {CO["group"]}.',img=None)]
    evs=sorted(EVENTS,key=lambda e:e['year'])
    for ev in evs:
        nodes.append(dict(y=str(ev['year']),t=ev['title'],img=ev['image']))
        if ev is [x for x in evs if x['year']==2024][-1]: nodes.append(dict(y='2024',t='MIPL celebrates its 10th anniversary with the whole team.',img='10th-anniversary-of-MIPL.jpg'))
    out=''; seen=set()
    for n in nodes:
        yr_cls='yr yr-sub' if n['y'] in seen else 'yr'; yr_txt=f'· {n["y"]}' if n['y'] in seen else n['y']; seen.add(n['y'])
        ph=(f'<div class="ph">{pic(n["img"],n["t"],R,sizes="420px")}</div>' if n['img'] else f'<div class="ph" style="display:flex;align-items:center;justify-content:center;background:var(--ink)"><img src="{R}assets/logo/mipl-logo-mark-dark.svg" alt="" width="120" height="111" style="width:34%"></div>')
        out+=f'<article class="tl-node"><p class="{yr_cls}">{yr_txt}</p><div class="dot"></div>{ph}<p>{e(n["t"])}</p></article>'
    return f'<div class="htl" aria-label="Company timeline"><div class="htl-track"><div class="htl-line" aria-hidden="true"><i></i></div>{out}</div></div>'

# ---------------- INDEX ----------------
def build_index():
    R=''
    intro=f'''<div id="intro" aria-hidden="true"><div class="door l"></div><div class="door r"></div><div class="stage">{logo_svg(ids=True,tm=True,hidden=True).replace('class="mlogo"','class="mlogo" id="ilogo"',1)}
<div class="wm" id="wm">{''.join('<span class="sp"></span>' if ch==' ' else f'<span>{ch}</span>' for ch in 'MAHARSHI INDUSTRIES')}</div></div><button class="skipintro" type="button">Skip intro</button></div>
<script>setTimeout(function(){{if(!window.__introDone){{var i=document.getElementById('intro');if(i)i.remove();document.body.classList.remove('lock');var n=document.querySelector('.nav .mlogo');if(n)n.style.opacity=1}}}},9000);</script>'''
    stack=''.join(f'''<article class="scard" style="--i:{i}"><div class="tx"><div><span class="num" aria-hidden="true">{L["n"]:02d}</span><h3>{e(LN(L))}</h3><p>{e(L["summary"])}</p></div>
<div><div class="chips" style="margin-bottom:18px">{"".join(f'<span class="chip">{e(p["name"].split(" (")[0])}</span>' for p in L["products"][:5])}</div><a class="btn magnetic" href="products/{L["slug"]}.html"><span class="lbl">Explore {e(L["short"])}</span> <span class="ar">→</span></a></div></div>
<div class="ph">{pic(L["hero"],LN(L),R,sizes="(max-width:900px) 100vw, 55vw")}</div></article>''' for i,L in enumerate(LINES))
    ring=''.join(f'<a class="rc" href="products/{s[3]}.html" style="--k:{i}"><span class="rph" data-cursor="Open">{pic(s[2],s[0],R,sizes="320px")}</span><span class="rtx"><span class="mono">{i+1:02d} · {e(s[1])}</span><b>{e(s[0])}</b></span></a>' for i,s in enumerate(SHOW))
    sect=''.join(f'<li><a href="products.html?sector={e(s)}" data-reveal-img="{full(SECTOR_IMG.get(s,"NDT-Boiler.jpg"),R)}"><span class="mono">{i+1:02d}</span><span class="t">{e(s)}</span><span class="go mono">{sum(1 for x in ALLP if s in x["tags"])} solutions ↗</span><span class="thumb">{pic(SECTOR_IMG.get(s,"NDT-Boiler.jpg"),"",R,sizes="100vw")}</span></a></li>' for i,s in enumerate(SECTORS))
    wall=''.join(f'<div class="lw" tabindex="0"><span class="lg"><img src="assets/img/client/{IM[client_img(c)]["base"].split("/")[-1]}.webp" alt="{e(cname(c))}" width="140" height="70" loading="lazy"></span><span class="nm">{e(cname(c))}</span></div>' for c in CLIENTS)
    vm=''.join(f'<span>{e(LN(L))}</span>' if i%2==0 else f'<span class="serif">{e(LN(L))}</span>' for i,L in enumerate(LINES))
    body=f'''
<section class="hero" data-theme="light"><div class="wrap"><div class="top"><div><p class="pill mono fade-in" style="margin-bottom:26px">Maharshi Industries · Since 2014</p>
<h1 class="h-xl" data-hsplit>Solution for a <span class="serif">smarter</span> world<span class="red">.</span></h1></div>
<div class="meta fade-in"><p class="mono">Robotics · BDDS · ROV · AR/VR<br>AI/ML · IoBT · Automation · SPM</p><p class="mono">Ahmedabad, India</p></div></div>
<div class="ctas fade-in"><a class="btn solid magnetic" href="products.html"><span class="lbl">Find a solution</span> <span class="ar">→</span></a><button class="btn magnetic" type="button" data-cmdk><span class="lbl">Quick search</span> <kbd class="mono" style="margin-left:4px">Ctrl K</kbd></button></div></div>
<div class="hmask"><div class="frame"><video autoplay muted loop playsinline preload="auto" poster="assets/video/poster.jpg" aria-hidden="true"><source src="assets/video/home-720.mp4" type="video/mp4" media="(max-width: 900px)"><source src="assets/video/home.mp4" type="video/mp4"></video></div>
<div class="cap"><p class="h-s">Robots, simulators and intelligent machines for the places people shouldn't have to go.</p><p class="mono">Scroll ↓</p></div></div></section>

<section class="sec" data-theme="dark"><div class="wrap"><p class="pill mono" style="margin-bottom:34px">(01) Company</p>
<p class="fill" data-fill>MIPL designs, integrates and delivers robotics, AI/ML, AR/VR and automation for <span class="serif">defence, nuclear, railways, oil &amp; gas</span> and public safety, from Ahmedabad since 2014.</p></div>
<div class="vmarq" style="margin-top:clamp(70px,12vh,130px)" aria-hidden="true"><div class="vtrack">{vm}{vm}</div></div></section>

<section class="sec" data-theme="light" id="lines"><div class="wrap"><div class="shead"><div><p class="pill mono">(02) Eight product lines</p><h2 class="h-l" data-split>Built for <span class="serif">critical</span> work.</h2></div><p class="lead" data-up>Scroll through all eight lines. Each card stacks on the last, from robotics to machinery built for the nuclear sector.</p></div>
<div class="stack">{stack}</div></div></section>

<section class="sec" data-theme="dark" id="lineup"><div class="wrap"><div class="shead"><div><p class="pill mono">(03) The lineup</p><h2 class="h-l" data-split>One from <span class="serif">every</span> line.</h2></div>
<div class="ring-ctl"><button class="btn magnetic" type="button" data-ring="-1" aria-label="Previous product"><span class="lbl">←</span></button><button class="btn magnetic" type="button" data-ring="1" aria-label="Next product"><span class="lbl">→</span></button></div></div>
<div class="ring3d" tabindex="0" aria-roledescription="carousel" aria-label="Product carousel. Use left and right arrow keys."><div class="ring">{ring}</div></div><p class="mono ring-live" aria-live="polite" style="text-align:center;margin-top:26px"></p></div></section>

<section class="explode" data-theme="dark" aria-label="Telescopic Manipulator, in detail"><div class="ex-head"><p class="pill mono" style="margin-bottom:14px">(04) Unpacked</p><h2 class="h-m">Telescopic <span class="serif">Manipulator</span></h2></div>
<div class="ex-stage"><div class="ex-main"><div class="ex-half l">{pic("TM ADGP.jpeg","Telescopic Manipulator demonstration",R,sizes="60vw")}</div><div class="ex-half r" aria-hidden="true">{pic("TM ADGP.jpeg","",R,sizes="60vw")}</div>
<div class="ex-core"><p class="mono" style="color:#ECEAE4">Bomb Detection &amp; Disposal</p><h3>Handles suspicious objects from a safe distance.</h3><p style="max-width:420px;color:#cfcdc6;font-size:15px">Grips objects as light as an egg without breakage. Folds into a portable wheeled case.</p><a class="btn magnetic" href="products/bomb-detection-disposal.html#telescopic-manipulator" style="margin-top:8px;color:#ECEAE4"><span class="lbl">Full specs</span> <span class="ar">→</span></a></div></div>
<div class="ex-layers"><div class="ex-layer" style="left:4%;bottom:6%">{pic("Telescopic-Manipulator-1-1536x864.jpg","Telescopic Manipulator with operators",R,sizes="300px")}</div>
<div class="ex-layer cut" style="right:4%;top:15%">{pic("bomb-home-img.jpg","Telescopic Manipulator claw",R,sizes="300px")}</div>
<div class="ex-layer" style="right:4%;bottom:6%">{pic("Training-Demonstartion-@-Tamilnadu-Commado-Force-1536x864.jpg","Training for Tamil Nadu Commando Force",R,sizes="300px")}</div></div>
<div class="ex-callouts"><div class="ex-callout" style="left:4%;top:32%"><b>5 m</b>Length fully extended · 900 mm collapsed</div><div class="ex-callout" style="left:4%;top:50%"><b>25 kg</b>Lifting capacity</div>
<div class="ex-callout" style="right:4%;top:50%;text-align:right"><b>6 h</b>Continuous operation on a Li-ion battery</div><div class="ex-callout" style="left:4%;bottom:6%;opacity:0" aria-hidden="true"></div></div></div></section>

<section class="sec counts-sec" data-theme="blue" id="numbers"><div class="p3d" data-3d="particles" aria-hidden="true"></div><div class="wrap" style="position:relative"><p class="pill mono" style="margin-bottom:30px">(05) By the numbers</p>
<div class="counts" data-stagger><div><p class="mono">Founded</p><p class="n" data-to="2014" data-from="1990">2014</p><p>Ahmedabad, Gujarat.</p></div><div><p class="mono">Product lines</p><p class="n" data-to="8">8</p><p>One team across robotics, AI, AR/VR and machinery.</p></div>
<div><p class="mono">Clients</p><p class="n" data-to="15">15</p><p>Defence, nuclear, research and railway organisations.</p></div><div><p class="mono">Sectors served</p><p class="n" data-to="{len(C["sectors"])}">{len(C["sectors"])}</p><p>From defence and nuclear to dairy and pharma.</p></div></div></div></section>

<section class="sec" data-theme="light" id="story" style="padding-bottom:0"><div class="wrap"><div class="shead"><div><p class="pill mono">(06) Our story</p><h2 class="h-l" data-split>2014 <span class="serif">onward</span>.</h2></div><p class="lead" data-up>From a workshop in Ahmedabad to installations with the Navy, Army, Railways and DRDO.</p></div></div>{htl(R)}<div style="height:clamp(60px,10vh,120px)"></div></section>

<section class="sec" data-theme="light" style="padding-top:0"><div class="wrap"><div class="shead"><div><p class="pill mono">(07) Workshop → field</p><h2 class="h-m" data-split>Built here. <span class="serif">Commissioned</span> there.</h2></div><p class="lead" data-up>VR Controlled Robotic System: drag the handle to compare our build with its commissioning at DRDO-INMAS (2023).</p></div>
<div class="ba" data-wipe="up">{pic("our-capabilities-img-12.jpg","VR controlled robot",R,sizes="100vw")}<div class="after">{pic("33d964dd-0f4c-4872-8400-5a13742e4152.jpg","VR controlled robotic system being commissioned at DRDO-INMAS",R,sizes="100vw")}</div>
<span class="tag l mono" style="color:#fff">Workshop</span><span class="tag r mono" style="color:#fff">DRDO-INMAS</span><div class="bar"></div><input type="range" min="0" max="100" value="50" aria-label="Compare workshop and field photos"><div class="knob" aria-hidden="true">⇆</div></div></div></section>

<section class="sec" data-theme="light" style="padding-top:0"><div class="wrap"><div class="shead"><div><p class="pill mono">(08) Sectors</p><h2 class="h-l" data-split>Where it <span class="serif">goes</span>.</h2></div><p class="lead" data-up>Pick a sector to open the product finder filtered to it.</p></div><ul class="rlist">{sect}</ul></div></section>

<section class="sec" data-theme="light" style="padding-top:0"><div class="wrap"><div class="shead"><div><p class="pill mono">(09) Trusted by</p><h2 class="h-m" data-split>15 organisations.</h2></div><a class="btn magnetic" href="clients.html"><span class="lbl">Clients &amp; deliveries</span> <span class="ar">→</span></a></div><div class="lwall" data-stagger>{wall}</div></div></section>

<section class="ending" data-theme="dark"><div class="wrap"><div class="logo3d" data-3d="logo"><img class="l3d-fallback" src="assets/logo/mipl-logo-dark.svg" alt="Maharshi Industries logo" width="300" height="248"></div>
<p class="pill mono" style="margin-bottom:24px">(10) Make in India</p><h2 class="big" data-split>Navnirmit <span class="serif">Bharat.</span></h2>
<div class="shead" style="margin:50px 0 0"><p class="lead">Aatma-Nirbhar Bharat · New India, Self-Reliant India. Tell us what you need built.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn solid magnetic" href="contact.html"><span class="lbl">Start a project</span> <span class="ar">→</span></a><a class="btn magnetic" href="mailto:info@miplsolns.com"><span class="lbl">info@miplsolns.com</span></a></div></div></div></section>'''
    page('index.html','MIPL — Maharshi Industries | Solution for a Smarter World','Maharshi Industries (MIPL), Ahmedabad: robotics, bomb detection & disposal, underwater ROVs, VR/AR simulators, AI/ML, IoBT, industrial automation and special purpose machinery since 2014.',body,R,'',extra=intro,three=True)

# ---------------- PRODUCTS (finder) ----------------
def build_products_index():
    R=''
    lchips=''.join(f'<button class="chip" type="button" data-f="line" data-v="{L["slug"]}" aria-pressed="false">{e(L["short"])}</button>' for L in LINES)
    schips=''.join(f'<button class="chip" type="button" data-f="sector" data-v="{e(s)}" aria-pressed="false">{e(s)}</button>' for s in SECTORS)
    lines=''.join(f'<li><a href="products/{L["slug"]}.html" data-reveal-img="{full(L["hero"],R)}"><span class="mono">{L["n"]:02d}</span><span class="t">{e(LN(L))}</span><span class="go mono">{len(L["products"])} ↗</span><span class="thumb">{pic(L["hero"],"",R,sizes="100vw")}</span></a></li>' for L in LINES)
    body=f'''<section class="ihero" data-theme="light"><div class="wrap"><p class="crumb mono"><a href="index.html">Home</a><span>/</span><span>Products</span></p>
<h1 class="h-xl" data-hsplit>Product <span class="serif">finder</span>.</h1><p class="lead" style="margin-top:26px">{len(ALLP)} solutions across eight lines. Filter by line or sector, or type to search.</p></div></section>
<section class="sec" data-theme="light" style="padding-top:20px" id="finder"><div class="wrap finder"><aside class="fpanel" aria-label="Filters">
<div><label class="mono" for="fq" style="display:block;margin-bottom:10px">Search</label><input id="fq" class="fsearch" type="search" placeholder="e.g. radiation, pipeline, VR" autocomplete="off"></div>
<fieldset><legend class="mono">Product line</legend><div class="chips"><button class="chip" type="button" data-f="line" data-v="all" aria-pressed="true">All lines</button>{lchips}</div></fieldset>
<fieldset><legend class="mono">Sector</legend><div class="chips"><button class="chip" type="button" data-f="sector" data-v="all" aria-pressed="true">All sectors</button>{schips}</div></fieldset>
<button class="btn" type="button" id="freset" style="align-self:flex-start">Reset filters</button></aside>
<div><div class="fcount"><p class="mono" id="fcount" role="status" aria-live="polite"></p><p class="mono">Sectors are tagged from each product's own description.</p></div>
<div class="cards">{''.join(pcard(x,R) for x in ALLP)}</div><p class="fempty">No matching solutions. Try another filter, or <a href="contact.html">ask us</a>.</p></div></div></section>
<section class="sec" data-theme="dark"><div class="wrap"><div class="shead"><div><p class="pill mono">Browse by line</p><h2 class="h-l" data-split>All eight <span class="serif">lines</span>.</h2></div></div><ul class="rlist">{lines}</ul></div></section>
<section class="sec" data-theme="light"><div class="wrap">{band(R,"Custom builds","Need something that doesn't exist yet?","contact.html","Tell us the problem")}</div></section>'''
    page('products.html','Products & finder | Maharshi Industries (MIPL)','Find MIPL solutions by product line or sector: robotics, BDDS, underwater ROV, VR & AR, AI & ML, IoBT, industrial automation and special purpose machinery.',body,R,'products.html')

# ---------------- PRODUCT LINE PAGES ----------------
def feats(lst): return '<div class="feats">'+''.join(f'<div><h4>{e(f["title"])}</h4><p>{e(f["text"])}</p></div>' for f in lst)+'</div>'
def prod_block(p,i,R,L):
    imgs=[u for u in (p.get('images') or [])+(p.get('media') or []) if u and has(u)]
    media=(f'<div class="media" data-wipe="{"left" if i%2 else "right"}">{pic(imgs[0],p["name"],R)}</div>' if imgs else f'<div class="media noimg" aria-hidden="true"><span class="mono" style="color:#cfcdc6">{e(p["name"])}</span><b>{i:02d}</b></div>')
    th=''
    if len(imgs)>1: th='<div class="thumbs">'+''.join(f'<button type="button" data-lb="{full(u,R)}" data-alt="{e(p["name"])}" aria-label="View photo {k+1} of {e(p["name"])}">{pic(u,"",R,sizes="80px")}</button>' for k,u in enumerate(imgs))+'</div>'
    pid=p['id']; tabs=[('Overview',f'<p style="font-size:18px">{e(p["description"])}</p><div class="chips" style="margin-top:18px">{"".join(f"<span class=chip>{e(t)}</span>" for t in tags(p,L))}</div>{th}')]
    if p.get('specs'): tabs.append(('Specifications','<ul class="speclist">'+''.join(f'<li>{e(s)}</li>' for s in p['specs'])+'</ul>'))
    if p.get('features'): tabs.append(('Features',feats(p['features'])))
    if p.get('industries'): tabs.append(('Industries',feats(p['industries'])))
    if p.get('useCases'): tabs.append(('Use cases','<div class="chips">'+''.join(f'<span class="chip">{e(u)}</span>' for u in p['useCases'])+'</div>'))
    tl=''.join(f'<button role="tab" id="t-{pid}-{k}" aria-controls="p-{pid}-{k}" aria-selected="{"true" if k==0 else "false"}" tabindex="{0 if k==0 else -1}">{t}</button>' for k,(t,_) in enumerate(tabs))
    tp=''.join(f'<div role="tabpanel" id="p-{pid}-{k}" aria-labelledby="t-{pid}-{k}" tabindex="0"{"" if k==0 else " hidden"}>{c}</div>' for k,(_,c) in enumerate(tabs))
    return f'<article class="prod2" id="{pid}">{media}<div><span class="mono">{i:02d} / {len(L["products"]):02d}</span><h2>{e(p["name"])}</h2><div class="tabs"><div role="tablist" aria-label="{e(p["name"])} details">{tl}</div>{tp}</div></div></article>'
def build_products():
    for k,L in enumerate(LINES):
        R='../'
        evs=[ev for ev in EVENTS if any(w in ev['title'] for w in L['kw'])]
        gal=[g for g in L['gallery'] if has(g)]
        why=''
        if L.get('why'): why='<section class="sec" data-theme="dark"><div class="wrap"><div class="shead"><div><p class="pill mono">Why MIPL</p><h2 class="h-l" data-split>Why <span class="serif">us</span>.</h2></div></div><div class="cards" data-stagger>'+''.join(f'<div class="pcard" data-tilt style="padding:26px;min-height:220px"><span class="mono">{j+1:02d}</span><h3 style="margin:30px 0 10px">{e(w["title"])}</h3><p>{e(w["text"])}</p></div>' for j,w in enumerate(L['why']))+'</div></div></section>'
        acc=''.join(f'<details><summary>{e(p["name"])}<span class="pl" aria-hidden="true"></span></summary><div class="ac-body">'+(('<ul class="speclist">'+''.join(f'<li>{e(s)}</li>' for s in p['specs'])+'</ul>') if p.get('specs') else '')+(feats(p['features']) if p.get('features') and not p.get('specs') else '')+(f'<p class="mut">{e(p["description"])}</p>' if not p.get('specs') and not p.get('features') else '')+f'<p style="margin-top:14px"><a class="mono" href="#{p["id"]}">Jump to {e(p["name"])} ↑</a></p></div></details>' for p in L['products'])
        rel=''
        if L.get('related'):
            s,n,dsc=L['related']; rel=f'<div class="band" style="margin:30px 0 0" data-up><div><p class="mono">Also see · Robotics</p><h2 class="h-s" style="margin-top:12px">{e(n)}</h2><p style="margin-top:10px;max-width:640px;opacity:.75">{e(dsc)}</p></div><a class="btn magnetic" href="{s}.html#minirov-eod"><span class="lbl">View in Robotics</span> <span class="ar">→</span></a></div>'
        galh=''
        if gal: galh='<section class="sec" data-theme="light" style="padding-top:40px"><div class="wrap"><div class="shead"><div><p class="pill mono">Gallery</p><h2 class="h-m" data-split>In the <span class="serif">field</span>.</h2></div><p class="mono">Click to enlarge</p></div><div class="gal" data-stagger>'+''.join(f'<button type="button" data-lb="{full(g,R)}" data-alt="{e(LN(L))}, photo {j+1}" aria-label="Open photo {j+1}">{pic(g,"",R,sizes="(max-width:900px) 50vw, 25vw")}</button>' for j,g in enumerate(gal))+'</div></div></section>'
        evh=''
        if evs: evh='<section class="sec" data-theme="light" style="padding-top:20px"><div class="wrap"><p class="pill mono" style="margin-bottom:26px">Related deliveries</p><ul class="rlist">'+''.join(f'<li><div class="row" data-reveal-img="{full(ev["image"],R)}"><span class="mono">{ev["year"]}</span><span class="t" style="font-size:clamp(20px,2vw,30px)">{e(ev["title"])}</span><span class="thumb">{pic(ev["image"],"",R,sizes="100vw")}</span></div></li>' for ev in evs)+'</ul></div></section>'
        prv=LINES[k-1]; nxt=LINES[(k+1)%8]
        body=f'''<section class="phero2" data-theme="light"><div class="wrap"><p class="crumb mono"><a href="../products.html">Products</a><span>/</span><span>{e(L["short"])}</span><span>· {L["n"]:02d} of 08</span></p>
<div class="grid"><div><h1 class="h-l" data-hsplit>{e(LN(L))}</h1>{f'<p class="lead" style="margin-top:22px;color:var(--fg)">{e(L["lead"])}</p>' if L.get("lead") else ''}<p class="lead" style="margin-top:18px">{e(L["intro"])}</p>
<div class="chips" style="margin-top:24px">{''.join(f'<span class="chip">{e(s)}</span>' for s in L["sectors"])}</div></div><div class="img" data-wipe="right">{pic(L["hero"],LN(L),R,eager=True,sizes="(max-width:900px) 100vw, 50vw")}</div></div></div></section>
<section data-theme="light"><div class="wrap"><nav class="subnav" aria-label="Products in this line">{''.join(f'<a class="chip" href="#{p["id"]}">{e(p["name"])}</a>' for p in L["products"])}</nav>{''.join(prod_block(p,i+1,R,L) for i,p in enumerate(L["products"]))}{rel}</div></section>
{why}{galh}{evh}
<section class="sec" data-theme="light" style="padding-top:20px"><div class="wrap two"><div><p class="pill mono">Quick reference</p><h2 class="h-m" data-split style="margin-top:20px">Specs at a <span class="serif">glance</span>.</h2></div><div class="acc">{acc}</div></div></section>
<section class="sec" data-theme="light" style="padding-top:0"><div class="wrap">{band(R,"Let's talk",f"Talk to us about {e(L['short'])}.",f"../contact.html?topic={L['slug']}","Start a conversation")}
<div class="pnav" style="margin-top:60px"><a href="{prv["slug"]}.html"><span class="mono">← Previous</span><b>{e(LN(prv))}</b></a><a href="{nxt["slug"]}.html"><span class="mono">Next →</span><b>{e(LN(nxt))}</b></a></div></div></section>'''
        page(f'products/{L["slug"]}.html',f'{LN(L)} | Maharshi Industries (MIPL)',L['summary'][:155],body,R,'products.html')

def build_about():
    R=''
    life=[l for l in C['lifeAtMipl'] if has(l['image'])]
    mas=''.join(f'<button type="button" data-lb="{full(l["image"],R)}" data-alt="{e(l["title"])}" aria-label="Open photo: {e(l["title"])}">{pic(l["image"],l["title"],R,sizes="(max-width:560px) 100vw, 33vw")}<span class="cap">{e(l["title"])}</span></button>' for l in life)
    acc=''.join(f'<details><summary>{e(LN(L))}<span class="pl" aria-hidden="true"></span></summary><div class="ac-body"><p class="mut" style="max-width:640px">{e(L["summary"])}</p><p style="margin-top:12px"><a class="btn" href="products/{L["slug"]}.html">Open {e(L["short"])} <span class="ar">→</span></a></p></div></details>' for L in LINES)
    body=f'''<section class="ihero" data-theme="light"><div class="wrap"><p class="crumb mono"><a href="index.html">Home</a><span>/</span><span>About</span></p><h1 class="h-xl" data-hsplit>Solution for a <span class="serif">smarter</span> world.</h1>
<div class="wipe-img" data-wipe="center" data-par>{pic("10th-anniversary-of-MIPL.jpg","The MIPL team at the 10th anniversary celebration",R,eager=True,sizes="100vw")}</div></div></section>
<section class="sec" data-theme="dark"><div class="wrap"><p class="fill" data-fill>{e(CO["intro"])}</p></div></section>
<section class="sec" data-theme="light"><div class="wrap two"><div><p class="pill mono">Who we are</p><h2 class="h-m" data-split style="margin-top:20px">Engineering for <span class="serif">critical</span> sectors.</h2></div><div class="body" data-up>{''.join(f"<p>{e(p)}</p>" for p in CO["about"])}</div></div>
<div class="wrap"><div class="facts" data-stagger><div><span class="mono">Founded</span><b data-to="2014" data-from="1990">2014</b></div><div><span class="mono">Group</span><b>{e(CO["group"])}</b></div><div><span class="mono">Based in</span><b>Ahmedabad</b></div><div><span class="mono">Anniversary</span><b><span data-to="10">10</span> years · 2024</b></div></div></div></section>
<section class="sec" data-theme="blue"><div class="wrap two"><div><p class="pill mono">Vision &amp; mission</p><h2 class="h-m" data-split style="margin-top:20px">Technology and <span class="serif">tradition</span>.</h2></div>
<div class="tabs"><div role="tablist" aria-label="Vision and mission"><button role="tab" id="t-vm-0" aria-controls="p-vm-0" aria-selected="true">Vision</button><button role="tab" id="t-vm-1" aria-controls="p-vm-1" aria-selected="false" tabindex="-1">Mission</button><button role="tab" id="t-vm-2" aria-controls="p-vm-2" aria-selected="false" tabindex="-1">Motto</button></div>
<div role="tabpanel" id="p-vm-0" aria-labelledby="t-vm-0" tabindex="0"><p class="lead" style="max-width:none">{e(CO["vision"])}</p></div><div role="tabpanel" id="p-vm-1" aria-labelledby="t-vm-1" tabindex="0" hidden><p class="lead" style="max-width:none">{e(CO["mission"])}</p></div>
<div role="tabpanel" id="p-vm-2" aria-labelledby="t-vm-2" tabindex="0" hidden><p class="h-m">{e(CO["motto"])}.</p><p class="lead" style="margin-top:14px">{e(CO["tagline"])} · {e(CO["taglineEn"])}.</p></div></div></div></section>
<section class="sec" data-theme="light" style="padding-bottom:0"><div class="wrap"><div class="shead"><div><p class="pill mono">Our story</p><h2 class="h-l" data-split>2014 <span class="serif">onward</span>.</h2></div></div></div>{htl(R)}<div style="height:10vh"></div></section>
<section class="sec" data-theme="light" style="padding-top:0"><div class="wrap two"><div><p class="pill mono">What we do</p><h2 class="h-m" data-split style="margin-top:20px">Eight <span class="serif">lines</span>.</h2></div><div class="acc">{acc}</div></div></section>
<section class="sec" data-theme="dark"><div class="wrap"><div class="shead"><div><p class="pill mono">Life @ MIPL</p><h2 class="h-l" data-split>The <span class="serif">people</span>.</h2></div><p class="mono">Click a photo to enlarge</p></div><div class="masonry">{mas}</div></div></section>
<section class="sec" data-theme="light"><div class="wrap">{band(R,"Make in India",e(CO["tagline"])+".","careers.html","Work with us")}</div></section>'''
    page('about.html','About | Maharshi Industries (MIPL)','Maharshi Industries Pvt. Ltd., part of the S.S.B.I group, Ahmedabad since 2014: defence and nuclear robotics, AI/ML, AR/VR and automation in line with Make in India.',body,R,'about.html')

def build_clients():
    R=''
    wall=''.join(f'<div class="lw" tabindex="0"><span class="lg"><img src="assets/img/client/{IM[client_img(c)]["base"].split("/")[-1]}.webp" alt="{e(cname(c))}" width="140" height="70" loading="lazy"></span><span class="nm">{e(cname(c))}</span></div>' for c in CLIENTS)
    rl=''.join(f'<li><button type="button" class="row" style="width:100%;text-align:left" data-lb="{full(ev["image"],R)}" data-alt="{e(ev["title"])}" data-reveal-img="{full(ev["image"],R)}"><span class="mono">{ev["year"]}</span><span class="t" style="font-size:clamp(20px,2.1vw,32px)">{e(ev["title"])}</span><span class="go mono">View ↗</span><span class="thumb">{pic(ev["image"],"",R,sizes="100vw")}</span></button></li>' for ev in EVENTS)
    body=f'''<section class="ihero" data-theme="light"><div class="wrap"><p class="crumb mono"><a href="index.html">Home</a><span>/</span><span>Clients</span></p><h1 class="h-xl" data-hsplit>Clients &amp; <span class="serif">deliveries</span>.</h1>
<p class="lead" style="margin-top:26px">MIPL works primarily with major government research organisations, defence forces and public-sector institutions across India.</p>
<div class="wipe-img" data-wipe="left" data-par>{pic("ValsuraEXPO.jpg","MIPL AI and VR showcase at INS Valsura",R,eager=True,sizes="100vw")}</div></div></section>
<section class="sec" data-theme="light"><div class="wrap"><div class="shead"><div><p class="pill mono">Logo wall</p><h2 class="h-l" data-split><span data-to="15">15</span> <span class="serif">organisations</span>.</h2></div><p class="mono">Hover or focus a logo</p></div><div class="lwall" data-stagger>{wall}</div></div></section>
<section class="sec" data-theme="dark"><div class="wrap"><div class="shead"><div><p class="pill mono">Deliveries &amp; milestones</p><h2 class="h-l" data-split>In the <span class="serif">field</span>.</h2></div><p class="mono">Hover to preview · click to enlarge</p></div><ul class="rlist">{rl}</ul></div></section>
<section class="sec" data-theme="light"><div class="wrap">{band(R,"Next delivery","Your project could be next.","contact.html","Contact us")}</div></section>'''
    page('clients.html','Clients & Deliveries | Maharshi Industries (MIPL)','Clients and recent deliveries of Maharshi Industries: DRDO-INMAS, BARC, Indian Navy, Indian Army, Indian Railways, NPCIL, NFC and more.',body,R,'clients.html')

def build_careers():
    R=''
    life=[l for l in C['lifeAtMipl'] if has(l['image'])]
    mas=''.join(f'<button type="button" data-lb="{full(l["image"],R)}" data-alt="{e(l["title"])}" aria-label="Open photo: {e(l["title"])}">{pic(l["image"],l["title"],R,sizes="(max-width:560px) 100vw, 33vw")}<span class="cap">{e(l["title"])}</span></button>' for l in life)
    areas=[('Robotics &amp; mechanical design','Robotic platforms, manipulators and fixtures, like our EOD, NDT and decontamination robots.'),('Embedded &amp; electronics','Control electronics, sensors and communication for systems that work in harsh conditions.'),('AR / VR development','Simulators and training modules for defence, nuclear, oil &amp; gas and education.'),('AI &amp; computer vision','Driver monitoring, predictive maintenance and surveillance intelligence.'),('Automation &amp; PLC','Control systems for industrial and nuclear-sector automation.'),('Fabrication &amp; assembly','Building, testing and commissioning special purpose machinery.')]
    acc=''.join(f'<details><summary>{a}<span class="pl" aria-hidden="true"></span></summary><div class="ac-body"><p class="mut">{t}</p></div></details>' for a,t in areas)
    body=f'''<section class="ihero" data-theme="light"><div class="wrap"><p class="crumb mono"><a href="index.html">Home</a><span>/</span><span>Careers</span></p><h1 class="h-xl" data-hsplit>Build what <span class="serif">matters</span>.</h1>
<div class="wipe-img" data-wipe="up" data-par>{pic("Life-@-MIPL-Celebration-with-entier-Team.jpeg","The MIPL team",R,eager=True,sizes="100vw")}</div></div></section>
<section class="sec" data-theme="dark"><div class="wrap"><p class="fill" data-fill>Work on robots, simulators and machines that go where people <span class="serif">shouldn't have to</span>, designed and built in Ahmedabad.</p></div></section>
<section class="sec" data-theme="light"><div class="wrap two"><div><p class="pill mono">Disciplines</p><h2 class="h-m" data-split style="margin-top:20px">Where you could <span class="serif">fit</span>.</h2><p class="lead" style="margin-top:20px">Our teams take products from idea to commissioning, so there is room to learn beyond your own discipline.</p></div><div class="acc">{acc}</div></div></section>
<section class="sec" data-theme="light" style="padding-top:0"><div class="wrap"><div class="shead"><div><p class="pill mono">Life @ MIPL</p><h2 class="h-m" data-split>Celebrations, trips and the <span class="serif">team</span>.</h2></div></div><div class="masonry">{mas}</div></div></section>
<section class="sec" data-theme="light" style="padding-top:0"><div class="wrap"><div class="band" data-up><div><p class="mono">Open roles</p><h2 class="h-m" style="margin-top:14px">No open roles are listed right now.</h2><p style="margin-top:12px;opacity:.75;max-width:620px">We're happy to hear from good engineers. Send your CV and a short note about what you'd like to build.</p><!-- TODO(MIPL): openings + HR email --></div><a class="btn solid magnetic" href="mailto:info@miplsolns.com?subject=Careers%20at%20MIPL"><span class="lbl">Email your CV</span> <span class="ar">↗</span></a></div></div></section>'''
    page('careers.html','Careers | Maharshi Industries (MIPL)','Careers at Maharshi Industries, Ahmedabad: robotics, AI, AR/VR and automation engineering for defence and nuclear sectors.',body,R,'careers.html')

def build_contact():
    R=''
    opts=''.join(f'<option value="{L["slug"]}">{e(LN(L))}</option>' for L in LINES)
    body=f'''<section class="ihero" data-theme="light"><div class="wrap"><p class="crumb mono"><a href="index.html">Home</a><span>/</span><span>Contact</span></p><h1 class="h-xl" data-hsplit>Let's <span class="serif">talk</span>.</h1><p class="lead" style="margin-top:26px">Tell us about your requirement. Our team will get back to you.</p></div></section>
<section class="sec" data-theme="light" style="padding-top:10px"><div class="wrap cgrid">
<!-- FORM SETUP: opens the visitor's email app (mailto) until you add a Formspree ID. Create a form at https://formspree.io and replace YOUR_FORM_ID. -->
<form id="cform" class="form" action="mailto:info@miplsolns.com" method="post" enctype="text/plain" data-endpoint="https://formspree.io/f/YOUR_FORM_ID" novalidate>
<div class="field"><label class="mono" for="f-name">Name *</label><input id="f-name" name="name" autocomplete="name" required aria-describedby="e-name"><p class="err" id="e-name">Please enter your name.</p></div>
<div class="field"><label class="mono" for="f-org">Organisation</label><input id="f-org" name="organisation" autocomplete="organization"></div>
<div class="field"><label class="mono" for="f-email">Email *</label><input id="f-email" name="email" type="email" autocomplete="email" required aria-describedby="e-email"><p class="err" id="e-email">Please enter a valid email.</p></div>
<div class="field"><label class="mono" for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
<div class="field full"><label class="mono" for="f-topic">Topic</label><select id="f-topic" name="topic"><option value="general">General enquiry</option>{opts}<option value="careers">Careers</option></select></div>
<div class="field full"><label class="mono" for="f-msg">Message *</label><textarea id="f-msg" name="message" required aria-describedby="e-msg"></textarea><p class="err" id="e-msg">Please write a short message.</p></div>
<div class="hp" aria-hidden="true"><label for="f-hp">Leave empty</label><input id="f-hp" name="company_website" tabindex="-1" autocomplete="off"></div>
<div class="full"><button class="btn solid magnetic" type="submit"><span class="lbl">Send message</span> <span class="ar">→</span></button></div></form>
<div class="cinfo"><div><span class="mono">Email</span><p><a href="mailto:{CT["email"]}">{CT["email"]}</a></p></div><div><span class="mono">Phone</span><p><a href="tel:+919727388634">{CT["mobile"]}</a><br>{"<br>".join(f'<a href="tel:+91{x.replace(" ","")[1:]}">{x}</a>' for x in CT["landlines"])}</p></div>
<div><span class="mono">Office</span><p>{e(CT["address"])}</p></div><div><span class="mono">Hours</span><p>{e(CT["hours"])}</p></div><div><span class="mono">Social</span><p><a href="{e(CT["linkedin"])}" target="_blank" rel="noopener">LinkedIn ↗</a></p></div></div></div>
<div class="wrap"><div class="map" data-src="{e(CT["mapEmbed"])}"><p class="mono">Map · Navrangpura, Ahmedabad</p><button id="loadmap" class="btn" type="button">Load Google Map</button><p class="mut" style="font-size:13px">Loads from Google and needs an internet connection.</p></div></div></section>'''
    page('contact.html','Contact | Maharshi Industries (MIPL)','Contact Maharshi Industries, Aarya Epoch, Navrangpura, Ahmedabad. info@miplsolns.com · +91 97273 88634.',body,R,'contact.html',sticky=False)

def build_404():
    body=f'''<section class="nf" data-theme="light">{logo_svg(label="Maharshi Industries logo")}<p class="mono">Error 404</p><h1 class="h-l">This page went <span class="serif">off-grid</span>.</h1><p class="lead" style="margin:0 auto">The page doesn't exist or has moved. Try search (<kbd>Ctrl K</kbd>).</p>
<div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center"><a class="btn solid magnetic" href="index.html"><span class="lbl">Home</span></a><button class="btn magnetic" type="button" data-cmdk><span class="lbl">Search</span></button><a class="btn" href="contact.html">Contact</a></div></section>'''
    page('404.html','Page not found | Maharshi Industries (MIPL)','The page you are looking for does not exist.',body,'')

build_index(); build_products_index(); build_products(); build_about(); build_clients(); build_careers(); build_contact(); build_404()
pages=['','products.html']+[f'products/{L["slug"]}.html' for L in LINES]+['about.html','clients.html','careers.html','contact.html']
open(OUT+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{DOMAIN}{p}</loc></url>\n' for p in pages)+'</urlset>\n')
print('ok', len(ALLP),'products', SECTORS)
