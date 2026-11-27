import json, os, html, urllib.parse
OUT='/workspace/MIPL-website-v2'
C=json.load(open('/workspace/mipl-mockup/antigravity/content.json'))
IM=json.load(open('/workspace/mipl-site-src/imgmap.json'))
P=json.load(open('/workspace/MIPL-logo-fix/work/P.json'))
DOMAIN='https://miplsolns.com/'
e=lambda s: html.escape(str(s),quote=True)
YEAR=2026

def rel_of(url_or_name):
    n=url_or_name.split('/img/')[-1] if '/img/' in url_or_name else url_or_name
    return urllib.parse.unquote(n)
def has(name): return rel_of(name) in IM
def pic(name,alt,R,cls='',eager=False,sizes='(max-width:900px) 100vw, 50vw',cut=None):
    m=IM[rel_of(name)]; b=R+'assets/img/'+m['base']
    iscut = m['alpha'] if cut is None else cut
    srcset=(f"{R}assets/img/{m['sm']} 800w, " if m['sm'] else '')+f"{b}.webp {m['w']}w"
    c=(cls+' '+('cut' if iscut else 'cov')).strip()
    ld='eager" fetchpriority="high' if eager else 'lazy'
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img class="{c}" src="{b}.{m["fb"]}" width="{m["w"]}" height="{m["h"]}" alt="{e(alt)}" loading="{ld}" decoding="async"></picture>')
def full(name,R):
    m=IM[rel_of(name)]; return f"{R}assets/img/{m['base']}.webp"

def logo_svg(ids=False,tm=False,cls='mlogo',label='Maharshi Industries logo',hidden=False):
    i=(lambda x:f' id="{x}"') if ids else (lambda x:'')
    vb='54 1 446 369' if tm else '54 1 398 369'
    a=' aria-hidden="true" focusable="false"' if hidden else f' role="img" aria-label="{label}"'
    t=f'<g class="tm"{i("mipl-tm")}><path d="{P["tm"]}"/></g>' if tm else ''
    return (f'<svg class="{cls}" viewBox="{vb}" xmlns="http://www.w3.org/2000/svg"{a}>'
      f'<g{i("mipl-blue")}><path{i("mipl-body-left")} class="bp" d="{P["body-left"]}"/><path{i("mipl-body-right")} class="bp" d="{P["body-right"]}"/><path{i("mipl-bar")} class="bar" d="{P["bar"]}"/></g>'
      f'<g{i("mipl-red")}><g{i("mipl-stem")} class="stem"><path d="{P["stem-top"]}"/><path d="{P["stem-base"]}"/></g><path{i("mipl-dot")} class="dot" d="{P["dot"]}"/></g>{t}</svg>')

cats={c['id']:c for c in C['productCategories']}
caps={c['id']:c for c in C['capabilities']}
rob=cats['robotics']; uw=[p for p in rob['products'] if p['id']=='underwater-rov'][0]
minirov=[p for p in rob['products'] if p['id']=='minirov-eod'][0]
first=lambda s: s.split('. ')[0].rstrip('.')+'.'
LINES=[
 dict(slug='robotics',title='Robotics',short='Robotics',cat='robotics',hero='VIGILBOT.jpg',
   intro=rob['intro'],summary=caps['robotics']['summary'],products=[p for p in rob['products'] if p['id']!='underwater-rov'],
   gallery=['Nuclear-Decontamination-robot.png','our-capabilities-img-12.jpg','NDT-Boiler.jpg','NDT-Oil-Gas.jpeg','NDT-Food-Industry.jpg','Fire-fight-1-1536x1021.jpg','MiniROV.jpg'],
   kw=['Robotic','Robot'],sectors=['Defence','Nuclear','Oil & Gas','Public Safety','Infrastructure']),
 dict(slug='bomb-detection-disposal',title='Bomb Detection & Disposal',short='BDDS',cat='bdds',hero='Telescopic-Manipulator-1-1536x864.jpg',
   intro=caps['bdds']['summary'],summary='Remote tools that let bomb disposal squads handle suspicious objects from a safe distance.',products=cats['bdds']['products'],
   gallery=['TM ADGP.jpeg','Training-Demonstartion-@-Tamilnadu-Commado-Force-1536x864.jpg','bomb-home-img.jpg','EOD-robot.png','CROT.png'],
   kw=['Telescopic'],related=('robotics','MiniROV – EOD Robot',minirov['description']),sectors=['Defence','Public Safety']),
 dict(slug='underwater-rov',title='Underwater ROV',short='Underwater ROV',cat='robotics',hero='WhatsApp-Image-2024-06-01-at-5.19.54-PM-1.jpeg',
   intro=uw['description'],summary=first(uw['description']),products=[uw],gallery=['WhatsApp-Image-2024-06-01-at-5.19.53-PM.jpeg'],kw=[],sectors=['Defence','Infrastructure','Public Safety']),
 dict(slug='vr-ar',title='VR & AR Simulations',short='VR & AR',cat='vr-ar',hero='VR-in-Defence.png',
   intro=cats['vr-ar']['intro'],summary=caps['vr-ar']['summary'],products=cats['vr-ar']['products'],why=cats['vr-ar'].get('why'),lead=cats['vr-ar'].get('lead'),
   gallery=['VR-simulation-photos-1.jpeg','VR-in-Oil-Gas-1.jpg','education-sector-img.jpeg','Indian Naval Acadamy.png','CST.png','5da076c1-d1c5-4121-b3a6-1c9ce695535d.jpg'],
   kw=['VR'],sectors=['Defence','Nuclear','Oil & Gas','Education','Supply Chain / Logistics','Railways']),
 dict(slug='ai-ml',title='AI & Machine Learning',short='AI & ML',cat='ai-ml',hero='AI-based-accident-prevention-3.jpg',
   intro=cats['ai-ml']['intro'],summary=caps['ai-ml']['summary'],products=cats['ai-ml']['products'],
   gallery=['DMS.jpg','RDAS.jpeg','Predictive-maintainace-phot-1536x827.jpg','027c6312-6ef7-454d-a728-a9d644b643f0.jpg','AI-based-accident-prevention-1.png'],
   kw=['AI ','RDAS','AI-based','AI based'],sectors=['Defence','Railways','Transportation','Oil & Gas']),
 dict(slug='iobt',title='IoBT — Internet of Battle Things',short='IoBT',cat='iobt',hero='Vitality-distress-Detection-system-IoBT.png',
   intro='Connected, wearable systems that keep commanders aware of the health, status and location of their teams in the field.',
   summary='Wearable systems that report the health, threats and location of personnel in real time.',products=cats['iobt']['products'],gallery=[],kw=[],sectors=['Defence','Public Safety'],generic_intro=True),
 dict(slug='industrial-automation',title='Industrial Automation',short='Automation',cat='industrial-automation',hero='SOR-GUi.jpeg',
   intro=cats['industrial-automation']['intro'],summary=cats['industrial-automation']['intro'],products=cats['industrial-automation']['products'],gallery=['industrial-img-3.jpg'],kw=[],sectors=['Nuclear','Oil & Gas']),
 dict(slug='special-purpose-machinery',title='Special Purpose Machinery',short='SPM',cat='spm',hero='Recent-Melter-Actual-Photo-scaled.jpeg',
   intro=cats['spm']['intro'],summary=first(cats['spm']['intro']),products=cats['spm']['products'],why=cats['spm'].get('why'),
   gallery=['ingot-unloading-system-img (1).jpg','Automatic-Basket-Placement-System-.png'],kw=[],sectors=['Nuclear','Infrastructure']),
]
for i,L in enumerate(LINES): L['n']=i+1

# showcase: one hero product per line
SHOW=[('Telescopic Manipulator','Bomb Detection & Disposal','Telescopic-Manipulator-1-1536x864.jpg','bomb-detection-disposal'),
 ('VIGILBOT','Robotics','VIGILBOT.jpg','robotics'),
 ('Underwater ROV','Underwater ROV','WhatsApp-Image-2024-06-01-at-5.19.54-PM-1.jpeg','underwater-rov'),
 ('VR Simulators','VR & AR','VR-in-Defence.png','vr-ar'),
 ('Accident Prevention','AI & ML','AI-based-accident-prevention-3.jpg','ai-ml'),
 ('Vitality & Distress Detection','IoBT','Vitality-distress-Detection-system-IoBT.png','iobt'),
 ('Shut-off Rod Automation','Industrial Automation','SOR-GUi.jpeg','industrial-automation'),
 ('Melter Dismantling System','Special Purpose Machinery','Recent-Melter-Actual-Photo-scaled.jpeg','special-purpose-machinery')]
SECTOR_IMG={'Defence':'VR-in-Defence.png','Nuclear':'Nuclear-Decontamination-robot.png','Railways':'RDAS.jpeg','Oil & Gas':'NDT-Oil-Gas.jpeg',
 'Public Safety':'Fire-fight-1-1536x1021.jpg','Transportation':'AI-based-accident-prevention-3.jpg','Education':'education-sector-img.jpeg',
 'Supply Chain / Logistics':'VR-simulation-photos-1.jpeg','Dairy':'NDT-Food-Industry.jpg','Pharma':'NDT-robot.png','Power Plants':'NDT-Boiler.jpg','Infrastructure':'WhatsApp-Image-2024-06-01-at-5.19.53-PM.jpeg'}
EVENTS=C['events']; CLIENTS=C['clients']; CO=C['company']; CT=C['contact']
def client_img(c): return rel_of(c['logo']).replace('client/','client/') if False else 'client/'+rel_of(c['logo']).split('/')[-1]
def cname(c): return c['name'].replace(' (identified from emblem; please confirm)','')

