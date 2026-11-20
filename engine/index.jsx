import React from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate, spring, Audio, staticFile, Img, Easing, Sequence} from 'remotion';

const YELLOW = '#FFD23F', CYAN = '#3DDCFF', GREEN = '#3DFF8B', RED = '#FF3D6E', NAVY = '#0b1033';
const DIFFC = {EASY: GREEN, MEDIUM: YELLOW, HARD: '#FF8A3D', EXPERT: RED, IMPOSSIBLE: '#B45CFF'};
const fontCss = `@font-face{font-family:'MX';src:url(${staticFile('montserrat-latin-900-normal.woff2')}) format('woff2');font-weight:900}
@font-face{font-family:'MX';src:url(${staticFile('montserrat-latin-800-normal.woff2')}) format('woff2');font-weight:800}`;
const F = (s, fps = 30) => Math.round(s * fps);
const pop = (fr, at) => spring({frame: fr - at, fps: 30, config: {damping: 11, stiffness: 160}});
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
const TITLES = {shape: ['GUESS THE COUNTRY', 'BY ITS SHAPE'], flag: ['GUESS THE FLAG', '3 SECONDS EACH'], capital: ['NAME THE CAPITAL', 'PICK THE RIGHT ONE'], size: ['WHICH IS BIGGER?', 'REAL SIZE COMPARISON'], emoji: ['GUESS THE COUNTRY', 'FROM 3 EMOJIS']};
const EMOJI_FONT = "'Noto Color Emoji', 'Apple Color Emoji', sans-serif";

const Background = ({w, h}) => {
  const fr = useCurrentFrame();
  const dots = [];
  for (let i = 0; i < 70; i++) {
    const x = (i * 137.5) % w, y = ((i * 97.3) % h + fr * (0.4 + (i % 5) * 0.15)) % h;
    dots.push(<circle key={i} cx={x} cy={h - y} r={1.5 + (i % 3)} fill="#fff" opacity={0.08 + (i % 4) * 0.03} />);
  }
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, #1b2a6b 0%, #0b1033 55%, #05061a 100%)'}}>
      <svg width={w} height={h} style={{position: 'absolute', opacity: 0.07}}>
        {Array.from({length: Math.ceil(h / 160) + 1}).map((_, i) => <line key={'h' + i} x1={0} x2={w} y1={i * 160} y2={i * 160} stroke="#fff" strokeWidth={2} />)}
        {Array.from({length: Math.ceil(w / 160) + 1}).map((_, i) => <line key={'v' + i} y1={0} y2={h} x1={i * 160} x2={i * 160} stroke="#fff" strokeWidth={2} />)}
      </svg>
      <svg width={w} height={h} style={{position: 'absolute'}}>{dots}</svg>
    </AbsoluteFill>
  );
};

const Header = ({p, idx, top = 150, scale = 1}) => {
  const [t1, t2] = p.title || TITLES[p.type];
  const n = p.scenes.length;
  return (
    <div style={{position: 'absolute', top, width: '100%', textAlign: 'center', fontFamily: 'MX', transform: `scale(${scale})`}}>
      <div style={{fontWeight: 900, fontSize: 78, color: '#fff', letterSpacing: 2, textShadow: '0 6px 0 #000'}}>{t1}</div>
      <div style={{fontWeight: 800, fontSize: 44, color: YELLOW, marginTop: 6}}>{t2}</div>
      {n <= 10 && <div style={{display: 'flex', justifyContent: 'center', gap: 18, marginTop: 34}}>
        {Array.from({length: n}).map((_, i) => {
          const done = idx !== null && i < idx, cur = idx === i;
          return <div key={i} style={{width: cur ? 70 : 34, height: 18, borderRadius: 9, background: done ? GREEN : cur ? YELLOW : 'rgba(255,255,255,0.22)'}} />;
        })}
      </div>}
    </div>
  );
};

const Caption = ({text, start, dur, top = 1360, size = 52, width = 900}) => {
  const fr = useCurrentFrame();
  if (fr < F(start)) return null;
  const words = text.split(' ');
  const shown = Math.min(words.length, Math.floor(((fr - F(start)) / F(dur)) * words.length) + 1);
  return (
    <div style={{position: 'absolute', top, width: '100%', display: 'flex', justifyContent: 'center'}}>
      <div style={{width, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', fontFamily: 'MX', fontWeight: 900, fontSize: size, lineHeight: 1.25, textShadow: '0 4px 0 #000, 0 0 18px rgba(0,0,0,.8)'}}>
        {words.map((w, i) => <span key={i} style={{display: 'inline-block', marginRight: 14, opacity: i < shown ? 1 : 0, color: i === shown - 1 ? YELLOW : '#fff'}}>{w.toUpperCase()}</span>)}
      </div>
    </div>
  );
};

const Ring = ({cdT, cd, size = 190}) => {
  const num = Math.max(1, Math.ceil(cd - cdT));
  const ringP = Math.min(1, Math.max(0, cdT / cd));
  const r = size * 0.42, c = size / 2;
  const ph = cdT % 1, sc = 1 + 0.25 * Math.max(0, 1 - ph * 3);
  return (
    <svg width={size} height={size}>
      <circle cx={c} cy={c} r={r} stroke="rgba(255,255,255,0.2)" strokeWidth={size * 0.074} fill="rgba(0,0,0,0.35)" />
      <circle cx={c} cy={c} r={r} stroke={num === 1 ? RED : YELLOW} strokeWidth={size * 0.074} fill="none" strokeLinecap="round"
        strokeDasharray={2 * Math.PI * r} strokeDashoffset={2 * Math.PI * r * ringP} transform={`rotate(-90 ${c} ${c})`} />
      <text x={c} y={c + size * 0.14} textAnchor="middle" fontFamily="MX" fontWeight={900} fontSize={size * 0.44} fill="#fff"
        style={{transform: `scale(${sc})`, transformOrigin: `${c}px ${c}px`}}>{num}</text>
    </svg>
  );
};

const Pill = ({iso2, label, s, fontSize = 84, flagW = 92}) => (
  <div style={{display: 'inline-flex', alignItems: 'center', gap: 22, padding: '14px 40px', background: '#fff', borderRadius: 24, boxShadow: '0 10px 0 rgba(0,0,0,.35)', transform: `scale(${s})`}}>
    {iso2 && <Img src={staticFile(`flags/${iso2}.svg`)} style={{width: flagW, height: flagW * 0.75, borderRadius: 8, border: `3px solid ${NAVY}`}} />}
    <span style={{fontFamily: 'MX', fontWeight: 900, fontSize, color: NAVY}}>{label.toUpperCase()}</span>
  </div>
);

const FactCard = ({text, s, fontSize = 40, maxWidth = 880}) => (
  <div style={{maxWidth, padding: '16px 30px', borderRadius: 20, background: 'rgba(61,220,255,0.15)', border: `4px solid ${CYAN}`, textAlign: 'center', fontFamily: 'MX', fontWeight: 800, fontSize, color: '#fff', transform: `scale(${s})`}}>
    <span style={{color: YELLOW}}>FUN FACT: </span>{text}
  </div>
);

const DiffChip = ({diff, s, fontSize = 40}) => diff ? (
  <div style={{padding: '10px 30px', borderRadius: 40, background: DIFFC[diff] || CYAN, color: NAVY, fontFamily: 'MX', fontWeight: 900, fontSize, transform: `scale(${s})`}}>{diff}</div>
) : null;

// ---------- question visuals ----------
const ShapeVisual = ({p, q, fr, L, size = 760, id}) => {
  const c = p.countries[q.iso2];
  const draw = interpolate(fr, [2, 26], [1, 0], {...clamp, easing: Easing.out(Easing.cubic)});
  const fillOp = interpolate(fr, [16, 30], [0, 1], clamp);
  const rev = fr >= L(q.reveal), revP = pop(fr, L(q.reveal));
  return (
    <svg width={size} height={size} viewBox="0 0 900 900">
      <defs><clipPath id={`c${id}`}><path d={c.d} /></clipPath>
        <filter id={`g${id}`}><feGaussianBlur stdDeviation="10" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter></defs>
      <path d={c.d} fill={rev ? 'none' : '#fff'} fillOpacity={fillOp} stroke={rev ? GREEN : CYAN} strokeWidth={rev ? 10 : 6} pathLength={1} strokeDasharray={1} strokeDashoffset={draw} filter={`url(#g${id})`} />
      {rev && <g clipPath={`url(#c${id})`} opacity={revP}><image href={staticFile(`flags/${q.iso2}.svg`)} x={0} y={0} width={900} height={900} preserveAspectRatio="xMidYMid slice" /></g>}
    </svg>
  );
};

const FlagVisual = ({q, fr, L, width = 760}) => {
  const e = pop(fr, 0);
  const rev = fr >= L(q.reveal);
  const flip = rev ? interpolate(fr, [L(q.reveal), L(q.reveal) + 8], [1, 1.06], clamp) : 1;
  return (
    <div style={{width, transform: `scale(${(0.8 + 0.2 * e) * flip}) rotate(${(1 - e) * -8}deg)`}}>
      <Img src={staticFile(`flags/${q.iso2}.svg`)} style={{width, height: width * 0.75, borderRadius: 28, border: `8px solid ${rev ? GREEN : '#fff'}`, boxShadow: rev ? `0 0 60px ${GREEN}` : '0 20px 60px rgba(0,0,0,.6)', objectFit: 'cover'}} />
    </div>
  );
};

const CapitalVisual = ({p, q, fr, L}) => {
  const rev = fr >= L(q.reveal);
  const e = pop(fr, 0);
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 34, fontFamily: 'MX'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 26, transform: `scale(${e})`}}>
        <Img src={staticFile(`flags/${q.iso2}.svg`)} style={{width: 170, height: 128, borderRadius: 14, border: '5px solid #fff'}} />
        <div style={{fontWeight: 900, fontSize: q.name.length > 12 ? 64 : 80, color: '#fff', textShadow: '0 6px 0 #000'}}>{q.name.toUpperCase()}</div>
      </div>
      {q.options.map((o, k) => {
        const s = pop(fr, 6 + k * 4); const ok = o === q.answer;
        const bg = rev ? (ok ? GREEN : 'rgba(255,255,255,0.08)') : 'rgba(255,255,255,0.12)';
        const col = rev ? (ok ? NAVY : 'rgba(255,255,255,0.35)') : '#fff';
        return (
          <div key={k} style={{width: 820, padding: '26px 34px', borderRadius: 22, background: bg, border: `4px solid ${rev && ok ? GREEN : 'rgba(255,255,255,0.35)'}`, display: 'flex', alignItems: 'center', gap: 28, transform: `scale(${s * (rev && ok ? 1 + 0.05 * pop(fr, L(q.reveal)) : 1)})`}}>
            <div style={{width: 62, height: 62, borderRadius: 31, background: rev && ok ? NAVY : YELLOW, color: rev && ok ? GREEN : NAVY, fontWeight: 900, fontSize: 38, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{'ABCD'[k]}</div>
            <div style={{fontWeight: 900, fontSize: 56, color: col}}>{o}</div>
          </div>
        );
      })}
    </div>
  );
};

const SizeVisual = ({p, q, fr, L, W = 1000, H = 760}) => {
  const A = p.countries[q.a], B = p.countries[q.b];
  const rev = fr >= L(q.reveal);
  const t = rev ? interpolate(fr, [L(q.reveal), L(q.reveal) + 22], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)}) : 0;
  const dims = [A, B].map(c => { const [[x0, y0], [x1, y1]] = c.true.bounds; return {x0, y0, w: x1 - x0, h: y1 - y0}; });
  const gap = 60, boxW = (W - gap) / 2;
  const indiv = dims.map(d => Math.min(boxW / d.w, (H - 120) / d.h));
  const common = Math.min((W - gap) / (dims[0].w + dims[1].w), (H - 120) / Math.max(dims[0].h, dims[1].h));
  const sc = indiv.map(s => s + (common - s) * t);
  const ws = dims.map((d, i) => d.w * sc[i]);
  const totalW = ws[0] + ws[1] + gap; const x0 = (W - totalW) / 2;
  const bigger = q.bigger;
  return (
    <svg width={W} height={H}>
      {[A, B].map((c, i) => {
        const d = dims[i], s = sc[i];
        const x = i === 0 ? x0 : x0 + ws[0] + gap;
        const y = (H - 120 - d.h * s) / 2 + 20;
        const win = rev && c.iso2 === bigger;
        const tx = Math.min(W - 230, Math.max(230, x + ws[i] / 2));
        const e = pop(fr, i * 5);
        return (
          <g key={i} opacity={e}>
            <g transform={`translate(${x} ${y}) scale(${s}) translate(${-d.x0} ${-d.y0})`}>
              <path d={c.true.d} fill={rev ? (win ? GREEN : '#ffffff') : '#ffffff'} fillOpacity={rev ? (win ? 0.95 : 0.55) : 0.92} stroke={i === 0 ? CYAN : YELLOW} strokeWidth={4 / s} />
            </g>
            <text x={tx} y={H - 50} textAnchor="middle" fontFamily="MX" fontWeight={900} fontSize={c.name.length > 11 ? 42 : 52} fill={i === 0 ? CYAN : YELLOW}>{c.name.toUpperCase()}</text>
            {rev && <text x={tx} y={H - 4} textAnchor="middle" fontFamily="MX" fontWeight={800} fontSize={34} fill="#fff" opacity={t}>{Math.round(c.area).toLocaleString('en-US')} km²</text>}
          </g>
        );
      })}
      {!rev && <text x={W / 2} y={H - 46} textAnchor="middle" fontFamily="MX" fontWeight={900} fontSize={54} fill="#fff" opacity={0.9}>VS</text>}
    </svg>
  );
};

const EmojiVisual = ({q, fr, L}) => {
  const rev = fr >= L(q.reveal), revP = pop(fr, L(q.reveal));
  return (
    <div style={{display: 'flex', gap: 34, justifyContent: 'center'}}>
      {q.emojis.map((em, k) => {
        const e = pop(fr, 4 + k * 9);
        const wob = rev ? 0 : Math.sin((fr + k * 11) / 7) * 3;
        return (
          <div key={k} style={{width: 290, height: 290, borderRadius: 40, background: 'rgba(255,255,255,0.12)', border: `5px solid ${rev ? GREEN : 'rgba(255,255,255,0.45)'}`, boxShadow: rev ? `0 0 40px ${GREEN}` : '0 18px 50px rgba(0,0,0,.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${e * (rev ? 1 + 0.04 * revP : 1)}) rotate(${wob}deg)`}}>
            <span style={{fontFamily: EMOJI_FONT, fontSize: 190, lineHeight: 1}}>{em}</span>
          </div>
        );
      })}
    </div>
  );
};

const AnswerLine = ({p, q}) => {
  if (p.type === 'capital') return {iso2: null, label: q.answer};
  if (p.type === 'size') { const c = p.countries[q.bigger]; return {iso2: c.iso2, label: c.name + ' wins'}; }
  return {iso2: q.iso2, label: q.name};
};

// ---------- SHORT ----------
const ShortQuestion = ({p, q}) => {
  const fr = useCurrentFrame();
  const L = (s) => F(s - q.start);
  const rev = fr >= L(q.reveal), revP = pop(fr, L(q.reveal));
  const cdT = (fr - L(q.countdown)) / 30, inCd = cdT >= 0 && !rev;
  const e = pop(fr, 0);
  const ans = AnswerLine({p, q});
  const shake = inCd && Math.ceil(p.cd - cdT) === 1 ? Math.sin(fr * 2.2) * 4 : 0;
  const isCap = p.type === 'capital';
  return (
    <AbsoluteFill>
      <Header p={p} idx={q.i} />
      {!isCap && <div style={{position: 'absolute', top: 470, width: '100%', display: 'flex', justifyContent: 'center'}}><DiffChip diff={q.diff} s={e} /></div>}
      <div style={{position: 'absolute', top: isCap ? 450 : 540, width: '100%', display: 'flex', justifyContent: 'center', transform: `translateX(${shake}px)`}}>
        {p.type === 'shape' && <div style={{transform: `scale(${0.85 + 0.15 * e + (rev ? 0.05 * revP : 0)})`}}><ShapeVisual p={p} q={q} fr={fr} L={L} id={q.i} /></div>}
        {p.type === 'flag' && <div style={{marginTop: 110}}><FlagVisual q={q} fr={fr} L={L} /></div>}
        {p.type === 'emoji' && <div style={{marginTop: 200}}><EmojiVisual q={q} fr={fr} L={L} /></div>}
        {p.type === 'size' && <div style={{marginTop: 20}}><SizeVisual p={p} q={q} fr={fr} L={L} /></div>}
        {isCap && <CapitalVisual p={p} q={q} fr={fr} L={L} />}
      </div>
      {inCd && <div style={{position: 'absolute', top: isCap ? 1400 : 1320, width: '100%', display: 'flex', justifyContent: 'center'}}><Ring cdT={cdT} cd={p.cd} /></div>}
      {rev && !isCap && <div style={{position: 'absolute', top: p.type === 'size' ? 1345 : 1320, width: '100%', textAlign: 'center'}}><Pill iso2={ans.iso2} label={ans.label} s={revP} fontSize={ans.label.length > 12 ? 64 : 84} /></div>}
      {rev && q.fVoice && fr >= L(q.fVoice) && <div style={{position: 'absolute', top: isCap ? 1410 : 1455, width: '100%', display: 'flex', justifyContent: 'center'}}><FactCard text={q.fact} s={pop(fr, L(q.fVoice))} /></div>}
      {!rev && !isCap && fr < L(q.countdown) && <Caption text={p.text['q' + q.i]} start={q.qVoice - q.start} dur={p.dur['q' + q.i]} />}
      {rev && p.type === 'size' && <Caption text={p.text['a' + q.i]} start={q.aVoice - q.start} dur={p.dur['a' + q.i]} top={1475} size={44} />}
    </AbsoluteFill>
  );
};

const ShortHook = ({p}) => {
  const fr = useCurrentFrame();
  const s = pop(fr, 2);
  const big = p.hookBig || 'ONLY 1%', small = p.hookSmall || (p.type === 'size' ? 'GET ALL 5 RIGHT' : `CAN NAME ALL ${p.scenes.length}`);
  const thumbs = p.scenes.slice(0, 5);
  return (
    <AbsoluteFill>
      <Header p={p} idx={null} />
      <div style={{position: 'absolute', top: 560, width: '100%', textAlign: 'center', fontFamily: 'MX', transform: `scale(${s})`}}>
        <div style={{fontSize: 150, fontWeight: 900, color: YELLOW, textShadow: '0 10px 0 #7a5a00'}}>{big}</div>
        <div style={{fontSize: 64, fontWeight: 900, color: '#fff', marginTop: 10}}>{small}</div>
      </div>
      <div style={{position: 'absolute', top: 960, width: '100%', display: 'flex', justifyContent: 'center', gap: 22}}>
        {thumbs.map((q, i) => {
          const e = pop(fr, 18 + i * 5);
          const c = p.countries[q.iso2 || q.a];
          return (
            <div key={i} style={{width: 170, height: 170, borderRadius: 24, background: 'rgba(255,255,255,0.1)', border: '3px solid rgba(255,255,255,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${e}) rotate(${(1 - e) * 30}deg)`, fontFamily: 'MX', fontWeight: 900, fontSize: 110, color: YELLOW}}>
              {p.type === 'shape' ? <svg width={150} height={150} viewBox="0 0 900 900"><path d={c.d} fill="#fff" opacity={0.9} /><text x={450} y={560} textAnchor="middle" fontSize={360} fill={NAVY}>?</text></svg> : p.type === 'emoji' && i === 0 ? <span style={{fontFamily: EMOJI_FONT, fontSize: 100}}>{q.emojis[0]}</span> : '?'}
            </div>
          );
        })}
      </div>
      <Caption text={p.text.hook} start={p.hook.voice} dur={p.dur.hook} />
    </AbsoluteFill>
  );
};

const ShortOutro = ({p}) => {
  const fr = useCurrentFrame();
  const s = pop(fr, 3);
  return (
    <AbsoluteFill>
      <Header p={p} idx={p.scenes.length} />
      <div style={{position: 'absolute', top: 520, width: '100%', textAlign: 'center', fontFamily: 'MX', transform: `scale(${s})`}}>
        <div style={{fontSize: 96, fontWeight: 900, color: '#fff', lineHeight: 1.05}}>HOW MANY<br />DID YOU GET?</div>
      </div>
      <div style={{position: 'absolute', top: 800, width: '100%', display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 26, padding: '0 70px', boxSizing: 'border-box'}}>
        {p.scenes.map((q, i) => {
          const e = pop(fr, 10 + i * 4);
          const iso = p.type === 'size' ? q.bigger : q.iso2;
          const c = p.countries[iso];
          const label = p.type === 'capital' ? q.answer : c.name;
          return (
            <div key={i} style={{width: 280, textAlign: 'center', transform: `scale(${e})`}}>
              {p.type === 'shape' ?
                <svg width={190} height={190} viewBox="0 0 900 900"><defs><clipPath id={`o${i}`}><path d={c.d} /></clipPath></defs>
                  <g clipPath={`url(#o${i})`}><image href={staticFile(`flags/${iso}.svg`)} width={900} height={900} preserveAspectRatio="xMidYMid slice" /></g><path d={c.d} fill="none" stroke="#fff" strokeWidth={8} /></svg>
                : <Img src={staticFile(`flags/${iso}.svg`)} style={{width: 200, height: 150, borderRadius: 14, border: '4px solid #fff', marginBottom: 12}} />}
              <div style={{fontFamily: 'MX', fontWeight: 900, fontSize: label.length > 11 ? 30 : 38, color: '#fff'}}>{label.toUpperCase()}</div>
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', top: 1400, width: '100%', textAlign: 'center', fontFamily: 'MX', fontWeight: 900, fontSize: 54, color: YELLOW, transform: `translateY(${Math.sin(fr / 5) * 8}px)`}}>COMMENT YOUR SCORE ↓</div>
    </AbsoluteFill>
  );
};

const Short = (p) => (
  <AbsoluteFill style={{backgroundColor: '#05061a'}}>
    <style>{fontCss}</style>
    <Background w={1080} h={1920} />
    <Sequence from={0} durationInFrames={F(p.hook.end)}><ShortHook p={p} /></Sequence>
    {p.scenes.map((q, i) => <Sequence key={i} from={F(q.start)} durationInFrames={F(q.end) - F(q.start)}><ShortQuestion p={p} q={q} /></Sequence>)}
    <Sequence from={F(p.outro.start)} durationInFrames={F(p.outro.end) - F(p.outro.start)}><ShortOutro p={p} /></Sequence>
    <Audio src={staticFile(`audio/${p.id}.wav`)} />
  </AbsoluteFill>
);

// ---------- LONG (16:9) ----------
const LongTop = ({p, idx}) => {
  const [t1] = p.title || TITLES[p.type];
  const n = p.scenes.length;
  const lv = idx === null ? null : p.levels.filter(l => l.start <= p.scenes[Math.min(idx, n - 1)].start).slice(-1)[0];
  return (
    <div style={{position: 'absolute', top: 40, left: 60, right: 60, display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: 'MX'}}>
      <div style={{fontWeight: 900, fontSize: 44, color: '#fff'}}>{t1} <span style={{color: YELLOW}}>· BORDERLINE QUIZ</span></div>
      {idx !== null && idx < n && <div style={{display: 'flex', gap: 18, alignItems: 'center'}}>
        {lv && <div style={{padding: '8px 22px', borderRadius: 30, background: DIFFC[lv.name] || CYAN, color: NAVY, fontWeight: 900, fontSize: 30}}>LEVEL {lv.level + 1}: {lv.name}</div>}
        <div style={{fontWeight: 900, fontSize: 40, color: '#fff'}}>{idx + 1}<span style={{opacity: .5}}>/{n}</span></div>
      </div>}
    </div>
  );
};

const LongQuestion = ({p, q}) => {
  const fr = useCurrentFrame();
  const L = (s) => F(s - q.start);
  const rev = fr >= L(q.reveal), revP = pop(fr, L(q.reveal));
  const cdT = (fr - L(q.countdown)) / 30, inCd = cdT >= 0 && !rev;
  const e = pop(fr, 0);
  const ans = AnswerLine({p, q});
  return (
    <AbsoluteFill>
      <LongTop p={p} idx={q.i} />
      <div style={{position: 'absolute', left: 120, top: 150, transform: `scale(${0.88 + 0.12 * e})`}}>
        {p.type === 'shape' && <ShapeVisual p={p} q={q} fr={fr} L={L} size={860} id={'L' + q.i} />}
        {p.type === 'flag' && <div style={{marginTop: 150}}><FlagVisual q={q} fr={fr} L={L} width={820} /></div>}
        {p.type === 'size' && <div style={{marginTop: 40}}><SizeVisual p={p} q={q} fr={fr} L={L} W={900} H={800} /></div>}
      </div>
      <div style={{position: 'absolute', left: 1080, top: 150, width: 760, height: 860, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 40, fontFamily: 'MX'}}>
        <div style={{fontWeight: 900, fontSize: 120, color: '#fff', opacity: 0.95, transform: `scale(${e})`}}>#{q.i + 1}</div>
        {!rev && <div style={{fontWeight: 800, fontSize: 46, color: YELLOW}}>{p.type === 'size' ? 'WHICH IS BIGGER?' : 'WHICH COUNTRY IS THIS?'}</div>}
        {inCd && <Ring cdT={cdT} cd={p.cd} size={230} />}
        {rev && <Pill iso2={ans.iso2} label={ans.label} s={revP} fontSize={ans.label.length > 12 ? 58 : 76} flagW={100} />}
        {rev && <div style={{fontWeight: 800, fontSize: 36, color: GREEN, opacity: revP}}>+1 POINT IF YOU GOT IT!</div>}
        {rev && q.fVoice && fr >= L(q.fVoice) && <FactCard text={q.fact} s={pop(fr, L(q.fVoice))} fontSize={36} maxWidth={720} />}
      </div>
    </AbsoluteFill>
  );
};

const LongLevel = ({lv, p}) => {
  const fr = useCurrentFrame();
  const s = pop(fr, 0);
  const n = p.levels.length;
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', fontFamily: 'MX'}}>
      <div style={{transform: `scale(${s})`, textAlign: 'center'}}>
        <div style={{fontWeight: 800, fontSize: 60, color: '#fff', opacity: .8}}>LEVEL {lv.level + 1} OF {n}</div>
        <div style={{fontWeight: 900, fontSize: 200, color: DIFFC[lv.name] || CYAN, textShadow: '0 12px 0 rgba(0,0,0,.4)'}}>{lv.name}</div>
      </div>
    </AbsoluteFill>
  );
};

const LongHook = ({p}) => {
  const fr = useCurrentFrame(); const s = pop(fr, 2);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', fontFamily: 'MX'}}>
      <LongTop p={p} idx={null} />
      <div style={{textAlign: 'center', transform: `scale(${s})`}}>
        <div style={{fontWeight: 900, fontSize: 130, color: '#fff'}}>{p.hookBig || `GUESS ${p.scenes.length} COUNTRIES`}</div>
        <div style={{fontWeight: 900, fontSize: 80, color: YELLOW, marginTop: 10}}>{p.hookSmall || 'EASY → IMPOSSIBLE'}</div>
        <div style={{fontWeight: 800, fontSize: 44, color: CYAN, marginTop: 40}}>GRAB A PEN · KEEP SCORE · {p.cd} SECONDS EACH</div>
      </div>
      <Caption text={p.text.hook} start={p.hook.voice} dur={p.dur.hook} top={900} size={44} width={1600} />
    </AbsoluteFill>
  );
};

const LongOutro = ({p}) => {
  const fr = useCurrentFrame(); const s = pop(fr, 3);
  const n = p.scenes.length;
  const sb = p.scoreboard || [[Math.round(n * .9), 'GEOGRAPHY GENIUS'], [Math.round(n * .7), 'WORLD TRAVELER'], [Math.round(n * .5), 'MAP EXPLORER'], [0, 'TOURIST']];
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', fontFamily: 'MX'}}>
      <div style={{textAlign: 'center', transform: `scale(${s})`}}>
        <div style={{fontWeight: 900, fontSize: 110, color: '#fff'}}>WHAT'S YOUR SCORE?</div>
        <div style={{marginTop: 40, display: 'flex', flexDirection: 'column', gap: 18, alignItems: 'center'}}>
          {sb.map(([min, label], i) => (
            <div key={i} style={{display: 'flex', gap: 30, alignItems: 'center', width: 1000, padding: '16px 36px', borderRadius: 20, background: 'rgba(255,255,255,0.08)', border: `3px solid ${[GREEN, YELLOW, '#FF8A3D', RED][i] || CYAN}`, transform: `scale(${pop(fr, 12 + i * 6)})`}}>
              <div style={{fontWeight: 900, fontSize: 52, color: [GREEN, YELLOW, '#FF8A3D', RED][i] || CYAN, width: 260, textAlign: 'left'}}>{min}{i === 0 ? `–${n}` : `+`}</div>
              <div style={{fontWeight: 900, fontSize: 52, color: '#fff'}}>{label}</div>
            </div>
          ))}
        </div>
        <div style={{marginTop: 40, fontWeight: 900, fontSize: 50, color: YELLOW}}>COMMENT YOUR SCORE & SUBSCRIBE FOR MORE ↓</div>
      </div>
    </AbsoluteFill>
  );
};

const Long = (p) => (
  <AbsoluteFill style={{backgroundColor: '#05061a'}}>
    <style>{fontCss}</style>
    <Background w={1920} h={1080} />
    <Sequence from={0} durationInFrames={F(p.hook.end)}><LongHook p={p} /></Sequence>
    {p.levels.map((lv, i) => <Sequence key={'l' + i} from={F(lv.start)} durationInFrames={F(lv.end) - F(lv.start)}><LongLevel lv={lv} p={p} /></Sequence>)}
    {p.scenes.map((q, i) => <Sequence key={i} from={F(q.start)} durationInFrames={F(q.end) - F(q.start)}><LongQuestion p={p} q={q} /></Sequence>)}
    <Sequence from={F(p.outro.start)} durationInFrames={F(p.outro.end) - F(p.outro.start)}><LongOutro p={p} /></Sequence>
    <Audio src={staticFile(`audio/${p.id}.wav`)} />
  </AbsoluteFill>
);

const meta = ({props}) => ({durationInFrames: Math.max(30, F(props.total || 1))});
const DEF = {total: 1, hook: {start: 0, voice: 0, end: 1}, scenes: [], levels: [], outro: {start: 0, voice: 0, end: 1}, text: {hook: ''}, dur: {hook: 1}, countries: {}, type: 'shape', id: 'x', cd: 3};
const Root = () => (<>
  <Composition id="Short" component={Short} width={1080} height={1920} fps={30} durationInFrames={30} defaultProps={DEF} calculateMetadata={meta} />
  <Composition id="Long" component={Long} width={1920} height={1080} fps={30} durationInFrames={30} defaultProps={DEF} calculateMetadata={meta} />
</>);
registerRoot(Root);
