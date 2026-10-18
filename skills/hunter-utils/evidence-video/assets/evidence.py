"""Evidence runner: a hash-chained manifest of real captures, and a HyperFrames
composition generated ONLY from that manifest. No frame in the manifest, no scene."""
import argparse, hashlib, json, os, re, shutil, struct, sys, time

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()

def img_size(p):
    with open(p,'rb') as f: d=f.read()
    if d[:8]==b'\x89PNG\r\n\x1a\n': w,h=struct.unpack('>II',d[16:24]); return w,h
    if d[:2]==b'\xff\xd8':
        i=2
        while i<len(d):
            if d[i]!=0xFF: i+=1; continue
            m=d[i+1]
            if m in (0xC0,0xC1,0xC2): h,w=struct.unpack('>HH',d[i+5:i+9]); return w,h
            i+=2+struct.unpack('>H',d[i+2:i+4])[0]
    raise SystemExit(f'unknown image format: {p}')

def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':')).encode()

def load(m):
    if os.path.exists(m): return json.load(open(m))
    return {'story':'', 'steps':[]}

def cmd_init(a):
    m={'story':a.story,'subject':a.subject,'capture_tool':a.tool,'started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'steps':[]}
    json.dump(m,open(a.manifest,'w'),indent=1); print('manifest initialised')

def cmd_add(a):
    m=load(a.manifest)
    if not os.path.exists(a.frame): raise SystemExit(f'ABORT: no capture for step "{a.title}" at {a.frame}')
    w,h=img_size(a.frame)
    step={'n':len(m['steps'])+1,'title':a.title,'action':a.action,'url':a.url,
          'captured_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(os.path.getmtime(a.frame))),
          'frame':{'path':os.path.relpath(a.frame,os.path.dirname(os.path.abspath(a.manifest))),'sha256':sha(a.frame),'w':w,'h':h},
          'focus':json.loads(a.focus) if a.focus else None,
          'network':json.load(open(a.network)) if a.network else [],
          'burp':json.loads(a.burp) if a.burp else [],
          'prev_sha256':m['steps'][-1]['sha256'] if m['steps'] else '0'*64}
    step['sha256']=hashlib.sha256(canon(step)).hexdigest()
    m['steps'].append(step); json.dump(m,open(a.manifest,'w'),indent=1)
    print(f"step {step['n']} {step['title']}: frame {step['frame']['sha256'][:12]} chain {step['sha256'][:12]}")

def cmd_verify(a):
    m=load(a.manifest); base=os.path.dirname(os.path.abspath(a.manifest)); prev='0'*64; ok=True
    for s in m['steps']:
        fp=os.path.join(base,s['frame']['path'])
        fs=sha(fp) if os.path.exists(fp) else None
        body={k:v for k,v in s.items() if k!='sha256'}
        chain=hashlib.sha256(canon(body)).hexdigest()
        good = fs==s['frame']['sha256'] and s['prev_sha256']==prev and chain==s['sha256']
        ok&=good; prev=s['sha256']
        print(f"{'OK ' if good else 'BAD'} step {s['n']} {s['title']}: frame {str(fs)[:12]} chain {chain[:12]}")
    print('CHAIN VALID' if ok else 'CHAIN BROKEN'); sys.exit(0 if ok else 1)

W,H=1920,1080
def esc(s): return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def cmd_build(a):
    m=load(a.manifest); base=os.path.dirname(os.path.abspath(a.manifest)); proj=a.project
    assets=os.path.join(proj,'assets'); os.makedirs(assets,exist_ok=True)
    http=json.load(open(a.http)) if a.http else None
    insight=json.load(open(a.insight)) if a.insight else m.get('insight')
    if not insight:
        sys.stderr.write('WARNING: no insight block — a story video must END with insight/impact/risk. Pass --insight or add m["insight"].\n')
    imap=(insight or {}).get('impact_map')
    T_TITLE,T_STEP,T_HTTP,T_CHAIN,T_INSIGHT,T_IMPACT,GAP=2.6,3.6,4.2,3.4,6.0,6.5,0.0
    scenes=[]; t=0.0
    scenes.append(('title',t,T_TITLE)); t+=T_TITLE
    for s in m['steps']:
        scenes.append(('step',t,T_STEP,s)); t+=T_STEP
        if http and s['n']==http.get('after_step'):
            scenes.append(('http',t,T_HTTP)); t+=T_HTTP
    scenes.append(('chain',t,T_CHAIN)); t+=T_CHAIN
    if insight:
        scenes.append(('insight',t,T_INSIGHT,insight)); t+=T_INSIGHT
    if imap:
        scenes.append(('impactmap',t,T_IMPACT,imap)); t+=T_IMPACT
    total=round(t,2)
    out=[]; tl_groups=[]; cur=[]
    def add(html):
        nonlocal cur
        cur=[]; out.append(html); tl_groups.append(cur)
    def tw(js): cur.append(js)
    add(f'''<section id="s-title" class="clip" data-start="0" data-duration="{T_TITLE}" data-track-index="0">
  <div class="bg"></div><div class="glow" id="g0" data-layout-allow-overflow></div>
  <div class="title-wrap"><div class="eyebrow" id="t-eye">USER STORY · EVIDENCE CHAIN</div>
  <h1 id="t-h1">{esc(m['story'])}</h1>
  <div class="meta" id="t-meta">{esc(m.get('subject',''))} · {len(m['steps'])} real captures · {esc(m.get('capture_tool',''))}</div></div>
</section>''')
    tw(f'tl.fromTo("#t-eye",{{y:24,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"power3.out"}},0.1);')
    tw(f'tl.fromTo("#t-h1",{{y:40,opacity:0}},{{y:0,opacity:1,duration:.7,ease:"power3.out"}},0.3);')
    tw(f'tl.fromTo("#t-meta",{{opacity:0}},{{opacity:1,duration:.5}},0.9);')
    tw(f'tl.to("#root .title-wrap",{{opacity:0,y:-30,duration:.35,ease:"power2.in"}},{T_TITLE-0.4});')
    for kind,st,dur,*rest in scenes:
        if kind!='step': continue
        s=rest[0]; n=s['n']; img=f"assets/frame-{n:02d}{os.path.splitext(s['frame']['path'])[1]}"
        shutil.copyfile(os.path.join(base,s['frame']['path']),os.path.join(proj,img))
        fw,fh=s['frame']['w'],s['frame']['h']
        cw,ch=1230,692; sc=min(cw/fw,ch/fh); dw,dh=fw*sc,fh*sc
        focus=s.get('focus'); punch=''
        if focus:
            cx=(focus['x']+focus['w']/2)*sc; cy=(focus['y']+focus['h']/2)*sc
            punch=f'''tl.fromTo("#f{n}-zoom",{{scale:1}},{{scale:1.6,duration:1.1,ease:"power2.inOut",transformOrigin:"{cx:.0f}px {cy:.0f}px"}},{0+1.4});
tl.fromTo("#f{n}-box",{{opacity:0,scale:1.3}},{{opacity:1,scale:1,duration:.45,ease:"back.out(2)"}},{0+1.2});'''
            box=f'<div class="focus-box" id="f{n}-box" style="left:{focus["x"]*sc:.0f}px;top:{focus["y"]*sc:.0f}px;width:{focus["w"]*sc:.0f}px;height:{focus["h"]*sc:.0f}px"></div>'
        else: box=''
        net=''.join(f'<li class="req" id="r{n}-{i}"><b class="m">{esc(r["method"])}</b><span class="u">{esc(r["path"])}</span><i class="st st-{str(r["status"])[0]}">{r["status"]}</i></li>' for i,r in enumerate(s['network'][:7]))
        add(f'''<section id="s{n}" class="clip" data-start="{st}" data-duration="{dur}" data-track-index="0">
  <div class="bg"></div><div class="glow" data-layout-allow-overflow></div>
  <div class="card" id="c{n}" style="width:{dw:.0f}px;height:{dh:.0f}px">
    <div class="chrome"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span class="url">{esc(s['url'])}</span></div>
    <div class="shot"><div class="zoom" id="f{n}-zoom" data-layout-allow-overflow><img src="{img}" width="{dw:.0f}" height="{dh:.0f}" alt="">{box}</div></div>
  </div>
  <aside class="panel" id="p{n}">
    <div class="num">{n:02d}<span>/{len(m['steps']):02d}</span></div>
    <h2>{esc(s['title'])}</h2>
    <p class="act">{esc(s['action'])}</p>
    <ul class="net">{net}</ul>
    <div class="hash"><span>frame sha256</span><code>{s['frame']['sha256'][:16]}…</code><span>captured</span><code>{esc(s['captured_at'])}</code></div>
  </aside>
</section>''')
        tw(f'tl.fromTo("#c{n}",{{x:-60,opacity:0}},{{x:0,opacity:1,duration:.55,ease:"power3.out"}},{0+0.05});')
        tw(f'tl.fromTo("#p{n} .num, #p{n} h2, #p{n} .act",{{y:26,opacity:0}},{{y:0,opacity:1,duration:.5,stagger:.08,ease:"power3.out"}},{0+0.25});')
        if s['network']: tw(f'tl.fromTo("#p{n} .req",{{x:30,opacity:0}},{{x:0,opacity:1,duration:.35,stagger:.09,ease:"power2.out"}},{0+0.8});')
        tw(f'tl.fromTo("#p{n} .hash",{{opacity:0}},{{opacity:1,duration:.4}},{0+1.6});')
        if punch: tw(punch)
        tw(f'tl.to("#root .card, #s{n} .panel",{{opacity:0,duration:.3,ease:"power2.in"}},{0+dur-0.32});')
    for kind,st,dur,*rest in scenes:
        if kind!='http': continue
        lines=http['lines']; hl=set(http.get('highlight',[]))
        code=''.join(f'<div class="ln{" hl" if i in hl else ""}" id="h-ln{i}">{esc(l)}</div>' for i,l in enumerate(lines))
        add(f'''<section id="s-http" class="clip" data-start="{st}" data-duration="{dur}" data-track-index="0">
  <div class="bg"></div><div class="glow" data-layout-allow-overflow></div>
  <div class="http-wrap"><div class="eyebrow" id="h-eye">{esc(http['eyebrow'])}</div>
  <h2 id="h-h2">{esc(http['title'])}</h2>
  <pre class="code" id="h-code">{code}</pre>
  <div class="meta" id="h-meta">{esc(http['meta'])}</div></div>
</section>''')
        tw(f'tl.fromTo("#h-eye, #h-h2",{{y:24,opacity:0}},{{y:0,opacity:1,duration:.5,stagger:.08,ease:"power3.out"}},{0+0.05});')
        tw(f'tl.fromTo("#h-code .ln",{{x:-20,opacity:0}},{{x:0,opacity:1,duration:.3,stagger:.07,ease:"power2.out"}},{0+0.5});')
        tw(f'tl.fromTo("#h-code .hl",{{backgroundColor:"rgba(124,92,255,0)"}},{{backgroundColor:"rgba(124,92,255,.28)",duration:.4}},{0+1.9});')
        tw(f'tl.fromTo("#h-meta",{{opacity:0}},{{opacity:1,duration:.4}},{0+2.3});')
        tw(f'tl.to("#root .http-wrap",{{opacity:0,duration:.3,ease:"power2.in"}},{0+dur-0.32});')
    cs=[x for x in scenes if x[0]=='chain'][0]; st=cs[1]; dur=cs[2]
    links=''.join(f'<div class="link" id="k{s["n"]}"><span class="kn">{s["n"]:02d}</span><code>{s["sha256"][:14]}</code><span class="arrow">→</span></div>' for s in m['steps'])
    add(f'''<section id="s-chain" class="clip" data-start="{st}" data-duration="{dur}" data-track-index="0">
  <div class="bg"></div><div class="glow" data-layout-allow-overflow></div>
  <div class="chain-wrap"><div class="eyebrow" id="k-eye">HASH CHAIN · {len(m['steps'])} STEPS</div>
  <div class="links">{links}<div class="link last" id="k-end"><span class="kn">✓</span><code>verify: evidence.py verify</code></div></div>
  <div class="meta" id="k-meta">Every frame is a real capture. Each step hashes the previous one. Swap one frame and the chain breaks.</div></div>
</section>''')
    tw(f'tl.fromTo("#k-eye",{{y:20,opacity:0}},{{y:0,opacity:1,duration:.45,ease:"power3.out"}},{0+0.05});')
    tw(f'tl.fromTo("#root .link",{{x:-30,opacity:0}},{{x:0,opacity:1,duration:.4,stagger:.16,ease:"power3.out"}},{0+0.3});')
    tw(f'tl.fromTo("#k-meta",{{opacity:0}},{{opacity:1,duration:.5}},{0+1.6});')
    tw(f'tl.fromTo("#root .glow",{{scale:1}},{{scale:1.15,duration:{dur},ease:"sine.inOut"}},0);')
    ins=[x for x in scenes if x[0]=='insight']
    if ins:
        _,st,dur,d=ins[0]; sev=(d.get('severity') or 'info').lower()
        checks=''.join(f'<li id="iv-{i}">{esc(c)}</li>' for i,c in enumerate(d.get('verify',[])))
        rows=[('INSIGHT','what the flow really is',d.get('insight','')),
              ('IMPACT','who is affected, what is at stake',d.get('impact','')),
              ('RISK','what to watch',d.get('risk',''))]
        cards=''.join(f'''<div class="irow" id="ir{i}"><div class="irlab">{lab}</div>
      <div class="irsub">{sub}</div><p class="irbody">{esc(body)}</p></div>''' for i,(lab,sub,body) in enumerate(rows))
        add(f'''<section id="s-insight" class="clip" data-start="{st}" data-duration="{dur}" data-track-index="0">
  <div class="bg"></div><div class="glow" data-layout-allow-overflow></div>
  <div class="ins-wrap"><div class="ins-head"><div class="eyebrow" id="i-eye">INSIGHT · IMPACT · RISK</div>
  <div class="sev sev-{sev}" id="i-sev">{esc(d.get('severity','info')).upper()}</div></div>
  <h2 id="i-h2">{esc(d.get('headline',''))}</h2>
  <div class="irows">{cards}</div>
  <ul class="verify" id="i-verify">{checks}</ul></div>
</section>''')
        tw(f'tl.fromTo("#i-eye",{{y:20,opacity:0}},{{y:0,opacity:1,duration:.45,ease:"power3.out"}},{0.05});')
        tw(f'tl.fromTo("#i-sev",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.5,ease:"back.out(2.5)"}},{0.3});')
        tw(f'tl.fromTo("#i-h2",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.6,ease:"power3.out"}},{0.4});')
        tw(f'tl.fromTo("#root .irow",{{x:-40,opacity:0}},{{x:0,opacity:1,duration:.5,stagger:.35,ease:"power3.out"}},{1.0});')
        if checks: tw(f'tl.fromTo("#root .verify li",{{opacity:0}},{{opacity:1,duration:.4,stagger:.2}},{2.6});')
        tw(f'tl.fromTo("#root .glow",{{scale:1}},{{scale:1.12,duration:{dur},ease:"sine.inOut"}},0);')
    imm=[x for x in scenes if x[0]=='impactmap']
    if imm:
        _,st,dur,g=imm[0]
        C=(295,540); Hb=(860,540); leaves=g['nodes'][:5]
        ys=[170,355,540,725,910][:len(leaves)]
        if len(leaves)<5:
            step=720/max(1,len(leaves)-1) if len(leaves)>1 else 0
            ys=[int(180+i*step) for i in range(len(leaves))] if len(leaves)>1 else [540]
        import math
        svg=[f'<circle class="ring" id="im-ring{i}" cx="{Hb[0]}" cy="{Hb[1]}" r="60" fill="none"/>' for i in range(3)]
        svg.append(f'<line class="edge e0" id="im-e0" x1="470" y1="540" x2="680" y2="540"/>')
        for i,y in enumerate(ys):
            ln=math.hypot(1300-1040, y-540)
            svg.append(f'<line class="edge e-{leaves[i].get("kind","data")}" id="im-e{i+1}" x1="1040" y1="540" x2="1300" y2="{y}" style="stroke-dasharray:{ln:.0f};stroke-dashoffset:{ln:.0f}"/>')
        nodes=[f'''<div class="node center" id="im-c" style="left:120px;top:480px;width:350px;height:120px">
      <div class="nlab">{esc(g['center']['label'])}</div><div class="nsub">{esc(g['center'].get('sub',''))}</div></div>''',
               f'''<div class="node hub" id="im-h" style="left:680px;top:473px;width:360px;height:134px">
      <div class="nlab">{esc(g['hub']['label'])}</div><div class="nsub">{esc(g['hub'].get('sub',''))}</div></div>''']
        for i,(lf,y) in enumerate(zip(leaves,ys)):
            nodes.append(f'''<div class="node leaf n-{lf.get('kind','data')}" id="im-l{i}" style="left:1300px;top:{y-64}px;width:510px;height:128px">
      <div class="nlab">{esc(lf['label'])}</div><div class="nsub">{esc(lf.get('sub',''))}</div></div>''')
        add(f'''<section id="s-impact" class="clip" data-start="{st}" data-duration="{dur}" data-track-index="0">
  <div class="bg"></div><div class="glow" data-layout-allow-overflow></div>
  <div class="imap-eye" id="im-eye">{esc(g.get('eyebrow','BLAST RADIUS · WHAT ONE SESSION REACHES'))}</div>
  <svg class="imap" viewBox="0 0 1920 1080" preserveAspectRatio="none" data-layout-allow-overflow>{''.join(svg)}</svg>
  {''.join(nodes)}
</section>''')
        tw(f'tl.fromTo("#im-eye",{{y:-20,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"power3.out"}},0.1);')
        tw(f'tl.fromTo("#im-c",{{scale:.7,opacity:0}},{{scale:1,opacity:1,duration:.5,ease:"back.out(2)"}},0.3);')
        tw(f'tl.fromTo("#im-e0",{{strokeDashoffset:210}},{{strokeDashoffset:0,duration:.4,ease:"power2.inOut"}},0.7);')
        tw(f'tl.fromTo("#im-h",{{scale:.7,opacity:0}},{{scale:1,opacity:1,duration:.5,ease:"back.out(2)"}},1.0);')
        for i in range(3):
            tw(f'tl.fromTo("#im-ring{i}",{{attr:{{r:70}},opacity:.5}},{{attr:{{r:360}},opacity:0,duration:2.4,ease:"sine.out",repeat:2}},{1.2+i*0.8});')
        for i in range(len(leaves)):
            tw(f'tl.to("#im-e{i+1}",{{strokeDashoffset:0,duration:.45,ease:"power2.out"}},{1.4+i*0.28});')
            tw(f'tl.fromTo("#im-l{i}",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"back.out(2.2)"}},{1.65+i*0.28});')

    CSS = """
:root{--bg:#0e1017;--bg2:#141826;--fg:#e9ecf5;--mute:#8b92a8;--acc:#7c5cff;--ok:#5bd39a;--warn:#f0b35c;--bad:#f06a6a}
#root{position:absolute;inset:0;overflow:hidden;color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
.bg{position:absolute;inset:0;background:radial-gradient(1200px 700px at 20% 110%,#1a1540 0%,var(--bg) 60%)}
.glow{position:absolute;width:900px;height:900px;left:1200px;top:-300px;border-radius:50%;background:radial-gradient(circle,rgba(124,92,255,.22),rgba(124,92,255,0) 65%)}
.eyebrow{font-size:22px;letter-spacing:.18em;color:var(--acc);font-weight:700}
.meta{color:var(--mute);font-size:24px;margin-top:28px}
.title-wrap{position:absolute;left:140px;right:140px;top:300px}
.title-wrap h1{font-size:84px;line-height:1.08;margin:22px 0 0;font-weight:800;letter-spacing:-.02em;max-width:1500px}
.card{position:absolute;left:80px;top:120px;border-radius:18px;overflow:hidden;background:var(--bg2);box-shadow:0 30px 80px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.06);display:flex;flex-direction:column}
.chrome{height:44px;display:flex;align-items:center;gap:8px;padding:0 16px;background:#1b2030;font-size:17px;color:var(--mute);font-family:ui-monospace,monospace;flex:none}
.dot{width:11px;height:11px;border-radius:50%;background:#2d3447;display:inline-block}
.chrome .url{margin-left:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.shot{position:relative;flex:1;overflow:hidden}
.zoom{position:absolute;inset:0;will-change:transform}
.zoom img{display:block;width:100%;height:100%;object-fit:cover}
.focus-box{position:absolute;border:4px solid var(--acc);border-radius:10px;box-shadow:0 0 0 4000px rgba(10,12,20,.35),0 0 30px rgba(124,92,255,.6)}
.panel{position:absolute;left:1360px;top:120px;width:480px;height:736px}
.num{font-size:96px;font-weight:800;letter-spacing:-.04em;line-height:1;color:var(--fg)}
.num span{font-size:36px;color:var(--mute);font-weight:600;margin-left:6px}
.panel h2{font-size:44px;line-height:1.1;margin:18px 0 10px;font-weight:800;letter-spacing:-.02em}
.act{font-size:24px;color:var(--mute);margin:0 0 26px;line-height:1.35}
.net{list-style:none;margin:0;padding:0;font-family:ui-monospace,monospace;font-size:18px}
.req{display:flex;gap:10px;align-items:baseline;padding:8px 10px;border-radius:8px;background:rgba(255,255,255,.035);margin-bottom:6px}
.req .m{color:#a98cff;width:58px;flex:none}
.req .u{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--fg)}
.req .st{font-style:normal;font-weight:700;flex:none} .st-2{color:var(--ok)} .st-3{color:var(--warn)} .st-4,.st-5{color:var(--bad)}
.hash{position:absolute;bottom:0;left:0;right:0;display:grid;grid-template-columns:auto 1fr;gap:4px 14px;font-size:17px;color:var(--mute)}
.hash code{font-family:ui-monospace,monospace;color:var(--fg)}
.http-wrap{position:absolute;left:140px;right:140px;top:110px}
.http-wrap h2{font-size:56px;margin:14px 0 26px;font-weight:800;letter-spacing:-.02em}
.code{margin:0;background:var(--bg2);border-radius:16px;padding:28px 34px;font-family:ui-monospace,monospace;font-size:26px;line-height:1.5;box-shadow:0 0 0 1px rgba(255,255,255,.06)}
.ln{white-space:pre;padding:0 10px;margin:0 -10px;border-radius:6px} .ln.hl{color:#fff}
.chain-wrap{position:absolute;left:140px;right:140px;top:220px}
.links{display:flex;flex-wrap:wrap;gap:22px 18px;margin-top:40px;align-items:center}
.link{display:flex;align-items:center;gap:14px;background:var(--bg2);border-radius:14px;padding:18px 24px;font-size:28px;box-shadow:0 0 0 1px rgba(255,255,255,.06)}
.link .kn{font-weight:800;color:var(--acc)} .link code{font-family:ui-monospace,monospace} .link .arrow{color:var(--mute)}
.link.last .kn{color:var(--ok)}
.ins-wrap{position:absolute;left:140px;right:140px;top:150px}
.ins-head{display:flex;align-items:center;justify-content:space-between}
.sev{font-size:22px;font-weight:800;letter-spacing:.1em;padding:10px 22px;border-radius:999px}
.sev-info{color:#8fb7ff;background:rgba(100,150,255,.14);box-shadow:0 0 0 1px rgba(100,150,255,.35)}
.sev-low{color:var(--ok);background:rgba(91,211,154,.12);box-shadow:0 0 0 1px rgba(91,211,154,.4)}
.sev-medium{color:var(--warn);background:rgba(240,179,92,.14);box-shadow:0 0 0 1px rgba(240,179,92,.45)}
.sev-high,.sev-critical{color:var(--bad);background:rgba(240,106,106,.15);box-shadow:0 0 0 1px rgba(240,106,106,.5)}
.ins-wrap h2{font-size:58px;line-height:1.1;margin:18px 0 36px;font-weight:800;letter-spacing:-.02em;max-width:1500px}
.irows{display:flex;flex-direction:column;gap:22px}
.irow{display:grid;grid-template-columns:260px 1fr;gap:10px 40px;padding:22px 0;border-top:1px solid rgba(255,255,255,.08)}
.irlab{font-size:30px;font-weight:800;letter-spacing:.04em;color:var(--acc)}
.irsub{grid-column:1;font-size:18px;color:var(--mute);margin-top:-4px}
.irbody{grid-column:2;grid-row:1 / span 2;margin:0;font-size:30px;line-height:1.4;color:var(--fg)}
.verify{list-style:none;margin:30px 0 0;padding:22px 0 0;border-top:1px solid rgba(255,255,255,.08);display:flex;flex-direction:column;gap:12px;font-size:24px;color:var(--mute)}
.verify li{padding-left:34px;position:relative}
.verify li::before{content:"↳";position:absolute;left:4px;color:var(--acc);font-size:22px;top:0}
.imap-eye{position:absolute;left:120px;top:70px;font-size:24px;letter-spacing:.16em;color:var(--acc);font-weight:800}
.imap{position:absolute;inset:0;width:100%;height:100%}
.ring{stroke:rgba(240,106,106,.5);stroke-width:2}
.edge{stroke:var(--acc);stroke-width:3;opacity:.85}
.edge.e-connector{stroke:var(--warn)} .edge.e-data{stroke:var(--bad)} .edge.e-session{stroke:#8fb7ff} .edge.e-project{stroke:var(--ok)} .edge.e-routine{stroke:var(--acc)}
.node{position:absolute;display:flex;flex-direction:column;justify-content:center;border-radius:16px;padding:0 28px;background:var(--bg2);box-shadow:0 20px 50px rgba(0,0,0,.5),0 0 0 1px rgba(255,255,255,.08);will-change:transform}
.node .nlab{font-size:30px;font-weight:800;letter-spacing:-.01em;line-height:1.1}
.node .nsub{font-size:20px;color:var(--mute);margin-top:6px;line-height:1.25}
.node.center{background:linear-gradient(135deg,#241a52,#141826);box-shadow:0 20px 60px rgba(124,92,255,.35),0 0 0 1px rgba(124,92,255,.5)}
.node.center .nlab{color:#cbb8ff}
.node.hub{background:linear-gradient(135deg,#1c2340,#141826);box-shadow:0 20px 60px rgba(124,92,255,.3),0 0 0 1px rgba(124,92,255,.4)}
.node.hub .nlab{font-size:34px}
.node.leaf{border-left:5px solid var(--acc)}
.node.n-connector{border-left-color:var(--warn)} .node.n-connector .nlab{color:#f0c58a}
.node.n-data{border-left-color:var(--bad)} .node.n-data .nlab{color:#f29a9a}
.node.n-session{border-left-color:#8fb7ff} .node.n-project{border-left-color:var(--ok)} .node.n-routine{border-left-color:var(--acc)}
"""
    comps=os.path.join(proj,'compositions'); os.makedirs(comps,exist_ok=True)
    hosts=[]
    for (kind,st,dur,*rest),html,tws in zip(scenes,out,tl_groups):
        sid=re.search(r'id="([^"]+)"',html).group(1); cid=f'sc-{sid}'
        inner=re.sub(r'^<section[^>]*>','',html.strip()); inner=re.sub(r'</section>$','',inner)
        local='\n'.join(t.replace('{ST}',f'{0}') for t in tws)
        sub=f"""<!doctype html>
<html><head><meta charset="UTF-8"></head><body>
<template>
<style>{CSS}</style>
<div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
{inner}
</div>
<script>
(() => {{
const tl = gsap.timeline({{ paused: true }});
{local}
window.__timelines["{cid}"] = tl;
}})();
</script>
</template>
</body></html>"""
        fn=f'compositions/{cid}.html'; open(os.path.join(proj,fn),'w').write(sub)
        hosts.append(f'<div id="{cid}" data-composition-id="{cid}" data-composition-src="{fn}" data-start="{st}" data-duration="{dur}" data-track-index="0" data-width="{W}" data-height="{H}"></div>')
    html=f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<title>{esc(m['story'][:60])}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>body{{margin:0;background:#0e1017}} #root{{position:relative;width:100%;height:100%;overflow:hidden}}</style>
</head><body>
<div id="root" data-composition-id="login-cowork" data-start="0" data-width="{W}" data-height="{H}" data-duration="{total}">
{chr(10).join(hosts)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
window.__timelines["login-cowork"] = tl;
</script>
</body></html>"""
    open(os.path.join(proj,'index.html'),'w').write(html)
    print(f'built {proj}/index.html: {len(scenes)} scenes, {total}s')

p=argparse.ArgumentParser(); sp=p.add_subparsers(dest='cmd',required=True)
q=sp.add_parser('init'); q.add_argument('--manifest',required=True); q.add_argument('--story',required=True); q.add_argument('--subject',default=''); q.add_argument('--tool',default='')
q=sp.add_parser('add'); q.add_argument('--manifest',required=True); q.add_argument('--title',required=True); q.add_argument('--action',required=True); q.add_argument('--url',default=''); q.add_argument('--frame',required=True); q.add_argument('--focus'); q.add_argument('--network'); q.add_argument('--burp')
q=sp.add_parser('verify'); q.add_argument('--manifest',required=True)
q=sp.add_parser('build'); q.add_argument('--manifest',required=True); q.add_argument('--project',required=True); q.add_argument('--http'); q.add_argument('--insight')
a=p.parse_args(); globals()['cmd_'+a.cmd](a)
