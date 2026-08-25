# Authoring reference - diagrams, screens, and layout

Read this before writing diagram functions. Everything here is already loaded by the engine in
`assets/template.html`; you only call it.

## Table of contents
- [The canvas](#the-canvas)
- [Helper API](#helper-api)
- [Screen object schema](#screen-object-schema)
- [Layout math (avoiding overlap)](#layout-math)
- [Worked example: one act](#worked-example)
- [Common mistakes](#common-mistakes)

## The canvas

Every diagram is a function returning `svg(inner)`. The viewBox is **640 wide × 300 tall**. Keep
content inside **x: 20–620, y: 30–270**. The right column holds the prose, so the diagram carries
*structure*, not sentences - short mono labels only.

Animate assembly with staggered `delay` (seconds). Left-to-right, ~0.15–0.3s apart, reads as the
idea building. The engine replays animations on every step change.

## Helper API

```js
svg(inner)                         // wrap your inner markup; adds arrowhead <defs>
box(x,y,w,h,label,sub,opts)        // rounded actor box. opts:{stroke,fill,tc,delay}
wire(x1,y1,x2,y2,opts)             // connector. opts:{color,marker:'ar'|'arA'|'arD',cls:'draw'|'flow',delay,w}
lbl(x,y,text,opts)                 // free label. opts:{color,anchor:'start'|'middle'|'end',fs,fw,delay}
seal(cx,cy,r,broken,delay)         // wax-seal glyph: check (broken=false) or crack (broken=true)
dQuiz()                            // ready-made "?" motif for quiz screens
```

Colour shortcuts available inside diagram functions: `A` (accent), `AI` (accent-ink, for text on
accent fills), `AS` (accent-soft fill), `H` (hairline), `P2` (panel-2 fill), `INK`, `MU` (muted),
`D` (danger), `W` (warn).

Conventions that keep the visual language consistent:
- **Accent** (`A`/`AS`/`AI`) = the good path, the verified/sealed/correct thing, the subject of the screen.
- **Danger** (`D`) = where it breaks, the attack, the wrong branch. Use `marker:'arD'` + often a dashed wire (`stroke-dasharray`) for an "attack" arrow, and `seal(...,true,...)` for "it shatters".
- **Warn** (`W`) = caution / "can only do the mild bad thing".
- **Neutral** (`P2`/`H`/`MU`) = ordinary actors and plumbing.
- Wires into an accent target use `marker:'arA'`; ordinary wires use `'ar'`.

Raw SVG is fine too when a helper doesn't fit (nested cards, lists, dials) - copy the `<g class="pop" style="animation-delay:Xs">…</g>` and `<text>` patterns from the examples. Use HTML entities, not literal Unicode (`&rarr;`, `&mdash;`, `&#10003;`, `&#8734;`), so the file stays charset-independent.

## Screen object schema

```js
// concept / feature / gotcha (default kind)
{ ey:'CONCEPT 1', eyt:'Topic', tag:'foundation'|'', chip:{label:'KEY',tone:'accent'|'warn'|'danger'},
  svg:dSomething, title:'A plain claim', body:'HTML…', aha:'the analogy', revealLabel:'reveal the intuition' }

// quiz
{ type:'quiz', ey:'GUT-CHECK', eyt:'Did it land?', tag:'trick question', svg:dQuiz,
  q:'Question?', opts:[{t:'wrong'},{t:'wrong'},{t:'right',correct:true}], explain:'why' }
```

- `ey` / `eyt`: eyebrow label + topic (top-left). Use `ey` to signal the act: `CONCEPT n`,
  `FEATURE`, `UNDER THE HOOD`, `DEEP DIVE`, `GUT-CHECK`, `RECAP`.
- `tag` vs `chip`: use `tag` for a muted top-right subtitle; use `chip` when a screen carries a
  labelled weight (`{label:'MEDIUM',tone:'warn'}` for a severity, `{label:'KEY',tone:'accent'}` for
  a takeaway). `chip` wins if both are present.
- `body`: HTML. `<span class="k">term</span>` for first-use jargon (renders as a mono chip),
  `<b>` for emphasis, `<br><br>` to separate beats (the body is a div, so block content is fine).
- `aha`: the reveal. Analogy or "so what", **not** more mechanics.
- `revealLabel`: button text. Default `reveal the intuition`; use `the fix`, `the takeaway`,
  `why it matters` to fit the screen.

## Layout math

The engine's box/label sizes are tuned for `font-size` 14 (box label), 10.5 (sublabel), 11 (free
label). To place things without collisions:

- A `box(x,y,w,h,...)`'s center is `(x+w/2, y+h/2)`; its label sits there, sublabel `+14` below.
- A horizontal wire between two boxes: `wire(x1+w1, cy, x2, cy)` where `cy` is the shared center y.
- Reserve the bottom band **y 240–270** for a one-line caption via `lbl(320, 255, '…')`.
- Three boxes across fit comfortably at widths ~120–150 with ~60px gaps: e.g. x = 40, 240, 460.
- A stacked pair of boxes (two lanes) at y = 78 and y = 176 leaves room for a caption at 262.
- Text you place with `lbl` is not measured - keep labels short (≤ ~28 chars) and give annotations
  their own clear region (above, below, or to the side of the drawing), never on top of a wire.

If a diagram feels crowded, it's two screens. Split it.

## Worked example

A three-screen act (concept → gotcha → quiz) for an imaginary "message queue" subject:

```js
function dQueue(){
  var i='';
  i+=box(30,124,120,54,'Producer','sends jobs',{delay:0});
  i+=wire(150,151,214,151,{delay:.3,color:A,marker:'arA'});
  i+=box(214,116,150,70,'Queue','holds in order',{stroke:A,fill:AS,tc:AI,delay:.4});
  i+=wire(364,151,428,151,{delay:.7,marker:'ar'});
  i+=box(428,124,150,54,'Worker','does the job',{delay:.8});
  i+=lbl(320,252,'work is buffered, not dropped',{color:MU,fs:11,delay:1.1});
  return svg(i);
}
function dPoison(){
  var i='';
  i+=box(214,116,150,70,'Queue',null,{stroke:A,fill:AS,tc:AI,delay:0});
  i+=wire(364,151,428,151,{delay:.3,color:D,marker:'arD'});
  i+=box(428,124,150,54,'Worker','crashes on it',{stroke:D,fill:'var(--danger-soft)',tc:D,delay:.5});
  i+=wire(428,124,289,116,{delay:.9,color:D,marker:'arD'}); // back to the queue
  i+=lbl(320,252,'a poison message loops forever',{color:D,fs:11,delay:1.2});
  return svg(i);
}

var steps=[
  {ey:'CONCEPT 1',eyt:'The queue',tag:'foundation',svg:dQueue,
   title:'A queue buffers work between producer and worker',
   body:'A <span class="k">producer</span> drops jobs onto a <span class="k">queue</span>; a <span class="k">worker</span> pulls them off in order. If the worker is slow, jobs wait instead of vanishing.',
   aha:'Like a <b>ticket spike</b> at a diner: orders pile in order, the cook works them one at a time, nothing gets lost in a rush.'},
  {ey:'DEEP DIVE',eyt:'Poison messages',chip:{label:'GOTCHA',tone:'warn'},svg:dPoison,
   title:'One bad message can jam the whole line',
   body:'If a job makes the worker crash, most queues put it <b>back</b> to retry &mdash; so it crashes the next worker too. That is a <span class="k">poison message</span>.',
   aha:'The fix is a <b>dead-letter queue</b>: after N failures, shunt the job aside so the line keeps moving.', revealLabel:'the fix'},
  {type:'quiz',ey:'GUT-CHECK',eyt:'Did it land?',tag:'trick question',svg:dQuiz,
   q:'Your workers keep crashing in a loop. What is the most likely cause?',
   opts:[{t:'The queue is too small'},{t:'A single poison message being retried',correct:true},{t:'Too many producers'}],
   explain:'A size limit drops or blocks new work; too many producers just fills the queue. A crash <b>loop</b> is the signature of one bad message being retried forever &mdash; the case for a dead-letter queue.'}
];
```

## Common mistakes

- **Cold terms.** A gotcha screen naming something the course never taught. Walk the ladder; every
  `<span class="k">…</span>` in a later screen should have first appeared, unhurried, on an earlier one.
- **Overlapping labels.** Two `lbl`/`box` texts sharing space. Give annotations their own band; if
  it's tight, split the screen. Always verify visually in the browser before publishing.
- **The reveal repeats the body.** The reveal must add the analogy or the payoff, not restate facts.
- **Rainbow diagrams.** More than ~3 colours reads as noise. Accent + neutral + one semantic.
- **Literal Unicode.** Use HTML entities so the file renders regardless of charset.
- **Shipping unverified.** Always serve it, open it, click a quiz, and read the console before publishing.
