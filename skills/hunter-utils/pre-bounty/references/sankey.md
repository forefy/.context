# Ranked Sankey + ranked-list templates

Two copy-paste widgets for the `visualize` `show_widget` tool. **Call the tool's
`read_me` once before your first `show_widget`** (it requires it) — modules
`["diagram","data_viz"]` are enough. Then fill the single `A = [...]` data array
in each template and render. Do not hand-author new diagram code per run — edit
the array only.

Shared conventions:
- One object per **in-scope** asset (drop out-of-scope ones or list them in prose).
- `v` = report volume / crowd proxy (thread width). If the program exposes no
  per-asset count, substitute an accessibility-based proxy and say so in prose.
- `r` = ROI verdict bucket: `Prime | Good | Recon | Skip | Dead`.
- `s` = setup tier key: `Trivial | Moderate | Hard`.
- `core` = 1 if top payout tier, else 0. `d` = short freshness date e.g. `"Jul '26"`.
- `fresh` = 1 to highlight a recent (e.g. current-year) rescope in green.
- `pick` = 1 to bold the label for a standout. Order the array **best→worst**.
- Colors are fixed so every run reads the same:
  `Prime #639922 · Good #378ADD · Recon #BA7517 · Skip #E24B4A · Dead #9A9A90`.
- Adjust the `$10k`/`$5k` ceiling strings to the actual program's top/half tier.

## Template 1 — ranked list (best→worst)

```html
<h2 style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;">Bug-bounty assets ranked best to worst by opportunity.</h2>
<div id="rk" style="width:100%;max-width:760px;margin:0 auto;padding:0.5rem 0;"></div>
<script>
(function(){
 const rows=[
  {r:1,n:'API & SDKs',v:'Prime',sc:92,m:'Top tier $$$ · ~2–4 hrs · 5% crowd · fresh',w:'Fresh top-tier + low barrier = get there first'},
  {r:2,n:'Native clients',v:'Prime',sc:87,m:'Top tier $$$ · 1–2 days · 7% crowd · stale',w:'Biggest setup moat at the top ceiling'}
  // ...one row per asset, ordered best->worst. v = verdict bucket, sc = 0-100 score
 ];
 const chip={Prime:['#C0DD97','#27500A'],Good:['#B5D4F4','#0C447C'],Recon:['#FAC775','#633806'],Skip:['#F7C1C1','#791F1F'],Dead:['#D3D1C7','#444441']};
 const bar={Prime:'#639922',Good:'#378ADD',Recon:'#BA7517',Skip:'#E24B4A',Dead:'#9A9A90'};
 let h='<div style="display:flex;align-items:center;gap:10px;padding:0 0 6px;font-size:11.5px;font-weight:500;color:var(--text-muted);"><div style="width:26px;"></div><div style="flex:1;">asset · setup · payout · crowd · freshness</div><div style="width:132px;text-align:right;">opportunity</div></div>';
 rows.forEach(function(o){
  const c=chip[o.v],b=bar[o.v];
  h+='<div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-top:1px solid var(--border);">'
   +'<div style="width:26px;height:26px;flex:none;border-radius:13px;background:'+c[0]+';color:'+c[1]+';font-size:12.5px;font-weight:500;display:flex;align-items:center;justify-content:center;">'+o.r+'</div>'
   +'<div style="flex:1;min-width:0;">'
    +'<div style="font-size:14px;color:var(--text-primary);"><span style="font-weight:500;">'+o.n+'</span> <span style="font-size:11px;color:'+c[1]+';background:'+c[0]+';border-radius:10px;padding:1px 7px;margin-left:4px;">'+o.v+'</span></div>'
    +'<div style="font-size:12px;color:var(--text-secondary);margin-top:2px;">'+o.m+'</div>'
    +'<div style="font-size:11.5px;color:var(--text-muted);margin-top:1px;">'+o.w+'</div>'
   +'</div>'
   +'<div style="width:132px;flex:none;display:flex;align-items:center;gap:7px;">'
    +'<div style="flex:1;height:8px;border-radius:4px;background:var(--surface-1);border:1px solid var(--border);overflow:hidden;"><div style="width:'+o.sc+'%;height:100%;background:'+b+';"></div></div>'
    +'<div style="width:22px;text-align:right;font-size:12px;color:var(--text-secondary);">'+o.sc+'</div>'
   +'</div>'
  +'</div>';
 });
 document.getElementById('rk').innerHTML=h;
})();
</script>
```

## Template 2 — ranked 3-stage Sankey (asset → setup → ROI)

Left column ordered best (top) → worst (bottom); setup and ROI nodes are
pre-ordered to minimize crossings for a rank-ordered left. Thread width = `v`.
Labels carry rank, volume, payout ceiling, and freshness date (green if `fresh`).

```html
<h2 style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;">Ranked Sankey of bug-bounty assets, best top to worst bottom, flowing through replication setup difficulty to ROI verdict; thread width is report volume.</h2>
<div id="sk" style="width:100%;padding:0.5rem 0;"></div>
<script>
(function(){
 const A=[
  {rk:1,n:'API & SDKs',v:20,s:'Moderate',r:'Prime',core:1,d:"Jul '26",fresh:1,pick:1},
  {rk:2,n:'Native clients',v:27,s:'Hard',r:'Prime',core:1,d:"May '25",pick:1}
  // ...one object per in-scope asset, ordered best->worst (rk = rank)
 ];
 const setups=[['Hard','Hard · 1–2 days'],['Moderate','Moderate · 2–4 hrs'],['Trivial','Trivial · under 15 min']];
 const rois=[['Prime','Prime — best ROI'],['Good','Good'],['Recon','Recon lane'],['Skip','Skip — crowded'],['Dead','Dead']];
 const rc={Skip:'#E24B4A',Dead:'#9A9A90',Recon:'#BA7517',Good:'#378ADD',Prime:'#639922'};
 const total=A.reduce((s,a)=>s+a.v,0)||1;
 const topPad=58,botPad=22,lx=316,c1=548,c2=756,bw=11,leftGap=5,gap=16,scale=1.3;
 const hOf=a=>Math.max(a.v*scale,14);
 let y=topPad;A.forEach(a=>{a.h=hOf(a);a.y0=y;y+=a.h+leftGap;});
 const leftEnd=y-leftGap;
 function lay(keys,f){let yy=topPad;const p={};keys.forEach(k=>{const h=A.filter(a=>f(a)===k).reduce((s,a)=>s+a.h,0);p[k]={y:yy,h:h,off:0};yy+=h+gap;});p.__end=yy-gap;return p;}
 const sp=lay(setups.map(x=>x[0]),a=>a.s);
 const rp=lay(rois.map(x=>x[0]),a=>a.r);
 A.forEach(a=>{a.sy=sp[a.s].y+sp[a.s].off;sp[a.s].off+=a.h;});
 A.forEach(a=>{a.ry=rp[a.r].y+rp[a.r].off;rp[a.r].off+=a.h;});
 const H=Math.ceil(Math.max(leftEnd,sp.__end,rp.__end)+botPad);
 function ribbon(x0,yA,x1,yB,h,c){const xc=(x0+x1)/2;return '<path d="M'+x0+','+yA+' C'+xc+','+yA+' '+xc+','+yB+' '+x1+','+yB+' L'+x1+','+(yB+h)+' C'+xc+','+(yB+h)+' '+xc+','+(yA+h)+' '+x0+','+(yA+h)+' Z" fill="'+c+'" fill-opacity="0.25"/>';}
 let s='';
 A.forEach(a=>{s+=ribbon(lx+bw,a.y0,c1,a.sy,a.h,rc[a.r]);});
 A.forEach(a=>{s+=ribbon(c1+bw,a.sy,c2,a.ry,a.h,rc[a.r]);});
 setups.forEach(k=>{const p=sp[k[0]];if(!p.h)return;s+='<rect x="'+c1+'" y="'+p.y+'" width="'+bw+'" height="'+p.h+'" rx="2" fill="#B4B2A9"/>';s+='<text x="'+c1+'" y="'+(p.y-6)+'" font-size="12.5" font-weight="500" fill="var(--text-primary)">'+k[1]+'</text>';});
 A.forEach(a=>{
  s+='<rect x="'+lx+'" y="'+a.y0+'" width="'+bw+'" height="'+a.h+'" rx="2" fill="'+rc[a.r]+'"/>';
  const ty=a.y0+a.h/2;
  const cap=a.core?'$10k':'$5k';
  const capF=a.core?'var(--text-primary)':'var(--text-muted)';
  const dF=a.fresh?'#639922':'var(--text-muted)';
  s+='<text x="'+(lx-8)+'" y="'+ty+'" text-anchor="end" dominant-baseline="middle" font-size="12.5" fill="var(--text-primary)">'
    +'<tspan fill="var(--text-muted)" font-weight="500">'+a.rk+'  </tspan>'
    +'<tspan font-weight="'+(a.pick?500:400)+'">'+a.n+'</tspan>'
    +'<tspan fill="var(--text-secondary)" font-weight="400">  '+a.v+'</tspan>'
    +'<tspan fill="var(--text-muted)">  ·  </tspan><tspan fill="'+capF+'" font-weight="'+(a.core?500:400)+'">'+cap+'</tspan>'
    +'<tspan fill="var(--text-muted)">  ·  </tspan><tspan fill="'+dF+'" font-weight="'+(a.fresh?500:400)+'">'+a.d+'</tspan>'
    +'</text>';
 });
 rois.forEach(k=>{const p=rp[k[0]];if(!p.h)return;const cnt=A.filter(a=>a.r===k[0]).reduce((x,a)=>x+a.v,0);const pct=Math.round(cnt/total*100);const c=rc[k[0]];s+='<rect x="'+c2+'" y="'+p.y+'" width="'+bw+'" height="'+p.h+'" rx="2" fill="'+c+'"/>';const ty=p.y+p.h/2;s+='<text x="'+(c2+bw+10)+'" y="'+(ty-7)+'" dominant-baseline="middle" font-size="13.5" font-weight="500" fill="var(--text-primary)">'+k[1]+'</text>';s+='<text x="'+(c2+bw+10)+'" y="'+(ty+11)+'" dominant-baseline="middle" font-size="11.5" fill="var(--text-secondary)">'+cnt+' reports · '+pct+'%</text>';});
 s+='<text x="'+(lx+bw)+'" y="26" text-anchor="end" font-size="11.5" font-weight="500" fill="var(--text-muted)">rank · asset · volume · ceiling · updated</text>';
 s+='<text x="'+(lx+bw)+'" y="42" text-anchor="end" font-size="10.5" fill="var(--text-muted)">top = best ROI · green date = fresh · $10k = top tier</text>';
 s+='<text x="'+c1+'" y="30" font-size="11.5" font-weight="500" fill="var(--text-muted)">replication setup</text>';
 s+='<text x="'+c2+'" y="30" font-size="11.5" font-weight="500" fill="var(--text-muted)">ROI verdict</text>';
 document.getElementById('sk').innerHTML='<svg viewBox="0 0 1020 '+H+'" width="100%" role="img" aria-label="Ranked Sankey best to worst: asset to setup to ROI verdict" style="max-width:1020px;display:block;margin:0 auto;font-family:var(--font-sans)">'+s+'</svg>';
})();
</script>
```

## Notes
- Tune only the `A` / `rows` arrays, the ceiling strings, and the `fresh`
  highlight rule. Geometry constants are calibrated for ~14 assets; for many
  more, lower `scale` or raise the viewBox width.
- Empty setup/ROI nodes auto-hide (`if(!p.h)return`), so you can drop buckets a
  given program doesn't need.
- Keep width = crowd. Swapping width to score loses the "crowd sits at the low
  barrier" story that makes the diagram land.
