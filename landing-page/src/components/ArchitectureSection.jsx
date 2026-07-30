import React, { useState } from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';

export function ArchitectureSection() {
  const [archRef, , revealStyle] = useScrollReveal();
  const [archStep, setArchStep] = useState(0);

  const archStepsData = [
    { key: 'fetch', n: '①', title: 'Fetch', icon: '⬇', body: "Pull the user's full transaction history and social graph from BMONI via the BMONIClient protocol. Two implementations: an in-memory stub backed by seed data for development, or the real BMONI sandbox adapter using httpx with x-api-key auth.", tags: ['protocol.py', 'stub.py', 'client.py'] },
    { key: 'profile', n: '②', title: 'Profile', icon: '◆', body: 'Aggregate raw transaction history into a UserProfile: recipient rollups (who, how much, how often), a 24-hour histogram of transfer times, the set of currencies ever used, and global amount statistics. This is the behavioral fingerprint.', tags: ['builder.py', 'RecipientRollup', 'UserProfile'] },
    { key: 'score', n: '③', title: 'Score', icon: '◎', body: 'Compute the DeviationVector — 8 signals across 4 dimensions (Recipient, Amount, Temporal, Categorical). Each scorer is a pure function: no external calls, no side effects, fully deterministic. The z_score_path tracks which z-score branch was used.', tags: ['DeviationVector', 'recipient.py', 'amount.py', 'temporal.py', 'categorical.py'] },
    { key: 'threshold', n: '④', title: 'Threshold', icon: '⚡', body: 'Apply configurable thresholds to decide SILENT_PASS or INTERVENE. Crucially: recipient_familiarity and graph_proximity are structural signals — they fire on any new recipient but cannot trigger INTERVENE alone. At least one non-structural signal must also fire.', tags: ['vector.py', 'fires()', 'should_intervene()'] },
    { key: 'synth', n: '⑤', title: 'Synthesize', icon: '✦', body: 'Only runs on INTERVENE. ClaudeSynthesizer calls Anthropic with a structured facts dict and a strict system prompt: "you are a mirror, not a judge". The validator blocks verdict keywords, unsourced numbers, and anything over 3 sentences. Failure falls back to the deterministic template.', tags: ['ClaudeSynthesizer', 'validator.py', 'template.py'] },
    { key: 'audit', n: '⑥', title: 'Audit', icon: '◉', body: "Fire-and-forget decision log back to BMONI. Records user_id, event_id, the decision, and the explanation. Errors in this step never affect the verdict — the user's transfer is never held up by a logging failure.", tags: ['log_decision()', 'fire-and-forget'] }
  ];

  const techPills = [
    { name: 'FastAPI', ver: '0.115' },
    { name: 'Pydantic', ver: '2.11' },
    { name: 'Anthropic SDK', ver: '0.49' },
    { name: 'httpx', ver: '0.28' },
    { name: 'NumPy', ver: '2.2' },
    { name: 'Uvicorn', ver: '0.34' },
    { name: 'pytest', ver: '8.3' },
    { name: 'Ruff', ver: '0.11' },
    { name: 'mypy', ver: '1.15' }
  ];

  const active = archStepsData[archStep];

  return (
    <section id="arch" data-screen-label="Architecture" ref={archRef} style={{
      position: 'relative',
      background: '#120a18',
      padding: 'clamp(72px, 9vw, 128px) clamp(18px, 5vw, 56px)',
      overflow: 'hidden'
    }}>
      <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(233,182,255,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(233,182,255,0.04) 1px,transparent 1px)', backgroundSize: '72px 72px', pointerEvents: 'none' }}></div>
      <div style={{ position: 'absolute', top: '14%', right: '5%', width: 'clamp(180px,22vw,340px)', height: 'clamp(180px,22vw,340px)', background: 'radial-gradient(circle, rgba(126,1,175,0.12) 0%, rgba(126,1,175,0) 70%)', filter: 'blur(80px)', pointerEvents: 'none' }}></div>
      <div style={{ position: 'absolute', bottom: '10%', left: '8%', width: 'clamp(200px,26vw,400px)', height: 'clamp(200px,26vw,400px)', background: 'radial-gradient(circle, rgba(198,95,232,0.08) 0%, rgba(198,95,232,0) 65%)', filter: 'blur(90px)', pointerEvents: 'none' }}></div>

      <div style={{ ...revealStyle, position: 'relative', maxWidth: '1320px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.14em', textTransform: 'uppercase', color: '#c65fe8' }}>
            Under the hood
          </span>
          <h2 style={{
            fontFamily: "'Archivo', sans-serif",
            fontWeight: 900,
            fontStretch: '125%',
            fontSize: 'clamp(20px, 6.2vw, 82px)',
            lineHeight: 0.86,
            letterSpacing: '-0.03em',
            textTransform: 'uppercase',
            color: '#e9d8f5',
            margin: '14px 0 0'
          }}>
            <span style={{ display: 'block', whiteSpace: 'nowrap' }}>Six stages,</span>
            <span style={{ display: 'block', whiteSpace: 'nowrap' }}>one verdict</span>
          </h2>
          <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '17px', lineHeight: 1.62, color: '#b9adc6', margin: '22px 0 0', maxWidth: '620px', textWrap: 'pretty' }}>
            Every transfer passes through a strict, ordered pipeline — from raw data to a single verdict. Select a stage to see what happens inside.
          </p>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: 0, flexWrap: 'wrap', marginTop: 'clamp(38px,4.5vw,56px)', position: 'relative' }}>
          {archStepsData.map((s, i) => {
            const on = i === archStep;
            return (
              <div key={s.key} style={{ display: 'flex', alignItems: 'center' }}>
                <button
                  onClick={() => setArchStep(i)}
                  style={{
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 12px',
                    background: 'transparent',
                    border: 'none',
                    font: 'inherit',
                    textAlign: 'center',
                    minWidth: '70px'
                  }}
                >
                  <div style={on ? {
                    width: '48px', height: '48px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: '#7e01af', color: '#fdf7ff', fontSize: '18px', transition: 'all .35s ease', boxShadow: '0 0 0 6px rgba(126,1,175,0.18)'
                  } : {
                    width: '48px', height: '48px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: 'transparent', border: '1.5px solid rgba(233,182,255,0.2)', color: '#665073', fontSize: '18px', transition: 'all .35s ease'
                  }}>
                    {s.icon}
                  </div>
                  <span style={on ? {
                    fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '110%', fontSize: '12px', letterSpacing: '.02em', textTransform: 'uppercase', color: '#f0e4f8', transition: 'color .3s ease'
                  } : {
                    fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '110%', fontSize: '12px', letterSpacing: '.02em', textTransform: 'uppercase', color: '#665073', transition: 'color .3s ease'
                  }}>
                    {s.title}
                  </span>
                </button>
                {i < archStepsData.length - 1 && (
                  <svg viewBox="0 0 24 12" style={{ width: '20px', height: '10px', flex: 'none', margin: '0 2px', opacity: 0.35 }}>
                    <path d="M2 6h18M16 2l4 4-4 4" fill="none" stroke="#c65fe8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"></path>
                  </svg>
                )}
              </div>
            );
          })}
        </div>

        <div style={{
          marginTop: '28px',
          background: 'rgba(42,10,61,0.45)',
          backdropFilter: 'blur(18px) saturate(140%)',
          WebkitBackdropFilter: 'blur(18px) saturate(140%)',
          border: '1px solid rgba(233,182,255,0.14)',
          borderRadius: '22px',
          padding: 'clamp(26px, 3.6vw, 44px)',
          display: 'grid',
          gridTemplateColumns: '1fr auto',
          gap: '32px',
          alignItems: 'center',
          boxShadow: '0 24px 60px rgba(8,2,14,0.5)'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '640px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.1em', color: '#c65fe8' }}>{active.n}</span>
              <h3 style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '110%', fontSize: 'clamp(22px, 2.4vw, 30px)', letterSpacing: '-0.01em', textTransform: 'uppercase', color: '#f0e4f8', margin: 0 }}>{active.title}</h3>
            </div>
            <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '16px', lineHeight: 1.65, color: '#c4b8cf', margin: 0, textWrap: 'pretty' }}>{active.body}</p>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '4px' }}>
              {active.tags.map((tag, idx) => (
                <span key={idx} style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.08em', padding: '5px 10px', borderRadius: '999px', background: 'rgba(126,1,175,0.3)', border: '1px solid rgba(233,182,255,0.18)', color: '#e9b6ff' }}>
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div style={{ width: '180px', height: '140px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {archStep === 0 && (
              <svg viewBox="0 0 180 140" style={{ width: '180px', height: '140px' }}>
                <rect x="6" y="10" width="74" height="58" rx="10" fill="#2a0a3d" stroke="rgba(233,182,255,0.18)" strokeWidth="1"></rect>
                <text x="43" y="36" fontFamily="IBM Plex Mono, monospace" fontSize="7" letterSpacing="0.08em" fill="#c65fe8" textAnchor="middle">BMONI</text>
                <text x="43" y="50" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299" textAnchor="middle">WALLET ENGINE</text>
                <rect x="100" y="10" width="74" height="58" rx="10" fill="#2a0a3d" stroke="rgba(233,182,255,0.18)" strokeWidth="1"></rect>
                <text x="137" y="36" fontFamily="IBM Plex Mono, monospace" fontSize="7" letterSpacing="0.08em" fill="#c65fe8" textAnchor="middle">SENTRI</text>
                <text x="137" y="50" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299" textAnchor="middle">COPROCESSOR</text>
                <path d="M80 30 L100 30" stroke="#c65fe8" strokeWidth="1.5" strokeDasharray="3 3" fill="none"></path>
                <path d="M100 48 L80 48" stroke="#8d8299" strokeWidth="1.5" strokeDasharray="3 3" fill="none"></path>
                <text x="90" y="24" fontFamily="IBM Plex Mono, monospace" fontSize="5" fill="#8d8299" textAnchor="middle">TXN</text>
                <text x="90" y="58" fontFamily="IBM Plex Mono, monospace" fontSize="5" fill="#8d8299" textAnchor="middle">HISTORY</text>
                <rect x="36" y="86" width="108" height="40" rx="8" fill="rgba(126,1,175,0.2)" stroke="rgba(233,182,255,0.25)" strokeWidth="1"></rect>
                <text x="90" y="103" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#e9b6ff" textAnchor="middle">TRANSACTION HISTORY</text>
                <text x="90" y="116" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299" textAnchor="middle">+ SOCIAL GRAPH</text>
              </svg>
            )}
            {archStep === 1 && (
              <svg viewBox="0 0 180 140" style={{ width: '180px', height: '140px' }}>
                <rect x="14" y="14" width="152" height="112" rx="12" fill="#2a0a3d" stroke="rgba(233,182,255,0.14)" strokeWidth="1"></rect>
                <text x="90" y="34" fontFamily="IBM Plex Mono, monospace" fontSize="7" letterSpacing="0.06em" fill="#c65fe8" textAnchor="middle">USER PROFILE</text>
                <line x1="30" y1="44" x2="150" y2="44" stroke="rgba(233,182,255,0.1)" strokeWidth="1"></line>
                <text x="36" y="60" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299">RECIPIENT ROLLUPS</text>
                <rect x="36" y="66" width="60" height="4" rx="2" fill="#7e01af"></rect>
                <rect x="100" y="66" width="40" height="4" rx="2" fill="#4c0a69"></rect>
                <text x="36" y="84" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299">HOUR HISTOGRAM</text>
                <rect x="36" y="90" width="8" height="16" rx="1" fill="#5c0f80"></rect>
                <rect x="48" y="94" width="8" height="12" rx="1" fill="#5c0f80"></rect>
                <rect x="60" y="86" width="8" height="20" rx="1" fill="#7e01af"></rect>
                <rect x="72" y="92" width="8" height="14" rx="1" fill="#5c0f80"></rect>
                <rect x="84" y="98" width="8" height="8" rx="1" fill="#4c0a69"></rect>
                <rect x="96" y="100" width="8" height="6" rx="1" fill="#3d0857"></rect>
                <text x="120" y="84" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299">CURRENCIES</text>
                <text x="120" y="96" fontFamily="IBM Plex Mono, monospace" fontSize="8" fill="#e9b6ff">NGN</text>
                <text x="142" y="96" fontFamily="IBM Plex Mono, monospace" fontSize="8" fill="#665073">USD</text>
              </svg>
            )}
            {archStep === 2 && (
              <svg viewBox="0 0 180 140" style={{ width: '180px', height: '140px' }}>
                <text x="90" y="16" fontFamily="IBM Plex Mono, monospace" fontSize="7" letterSpacing="0.06em" fill="#c65fe8" textAnchor="middle">DEVIATION VECTOR</text>
                <rect x="10" y="26" width="76" height="46" rx="8" fill="rgba(126,1,175,0.25)" stroke="rgba(233,182,255,0.15)" strokeWidth="1"></rect>
                <text x="48" y="42" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#e9b6ff" textAnchor="middle">RECIPIENT</text>
                <text x="48" y="56" fontFamily="IBM Plex Mono, monospace" fontSize="9" fill="#f0e4f8" textAnchor="middle">×2</text>
                <rect x="94" y="26" width="76" height="46" rx="8" fill="rgba(126,1,175,0.25)" stroke="rgba(233,182,255,0.15)" strokeWidth="1"></rect>
                <text x="132" y="42" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#e9b6ff" textAnchor="middle">AMOUNT</text>
                <text x="132" y="56" fontFamily="IBM Plex Mono, monospace" fontSize="9" fill="#f0e4f8" textAnchor="middle">×3</text>
                <rect x="10" y="80" width="76" height="46" rx="8" fill="rgba(126,1,175,0.25)" stroke="rgba(233,182,255,0.15)" strokeWidth="1"></rect>
                <text x="48" y="96" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#e9b6ff" textAnchor="middle">TEMPORAL</text>
                <text x="48" y="110" fontFamily="IBM Plex Mono, monospace" fontSize="9" fill="#f0e4f8" textAnchor="middle">×1</text>
                <rect x="94" y="80" width="76" height="46" rx="8" fill="rgba(126,1,175,0.25)" stroke="rgba(233,182,255,0.15)" strokeWidth="1"></rect>
                <text x="132" y="96" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#e9b6ff" textAnchor="middle">CATEGORICAL</text>
                <text x="132" y="110" fontFamily="IBM Plex Mono, monospace" fontSize="9" fill="#f0e4f8" textAnchor="middle">×2</text>
                <text x="90" y="136" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#665073" textAnchor="middle">8 SIGNALS · 4 DIMENSIONS</text>
              </svg>
            )}
            {archStep === 3 && (
              <svg viewBox="0 0 180 140" style={{ width: '180px', height: '140px' }}>
                <circle cx="90" cy="60" r="44" fill="none" stroke="rgba(233,182,255,0.15)" strokeWidth="1"></circle>
                <circle cx="90" cy="60" r="30" fill="none" stroke="rgba(126,1,175,0.4)" strokeWidth="1.5" strokeDasharray="4 3"></circle>
                <circle cx="72" cy="48" r="4" fill="#5c0f80"></circle>
                <circle cx="102" cy="53" r="4" fill="#5c0f80"></circle>
                <circle cx="85" cy="75" r="4" fill="#5c0f80"></circle>
                <circle cx="118" cy="72" r="5" fill="#c65fe8"></circle>
                <circle cx="118" cy="72" r="9" fill="none" stroke="#c65fe8" strokeWidth="1" opacity="0.5"></circle>
                <text x="90" y="118" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299" textAnchor="middle">STRUCTURAL VS NON-STRUCTURAL</text>
                <text x="90" y="130" fontFamily="IBM Plex Mono, monospace" fontSize="7" fill="#e9b6ff" textAnchor="middle">PASS · INTERVENE</text>
              </svg>
            )}
            {archStep === 4 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '160px' }}>
                <div style={{ padding: '12px 14px', background: '#2a0a3d', borderRadius: '12px 12px 12px 4px', display: 'flex', flexDirection: 'column', gap: '5px' }}>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '8px', letterSpacing: '.08em', color: '#c65fe8' }}>CLAUDE HAIKU</span>
                  <div style={{ width: '90%', height: '4px', background: 'rgba(233,182,255,0.4)', borderRadius: '2px' }}></div>
                  <div style={{ width: '100%', height: '4px', background: 'rgba(233,182,255,0.4)', borderRadius: '2px' }}></div>
                  <div style={{ width: '55%', height: '4px', background: 'rgba(233,182,255,0.4)', borderRadius: '2px' }}></div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '0 4px' }}>
                  <svg viewBox="0 0 12 12" style={{ width: '10px', height: '10px', flex: 'none' }}><path d="M2 6l3 3 5-5" fill="none" stroke="#c65fe8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"></path></svg>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '7px', letterSpacing: '.06em', color: '#8d8299' }}>VALIDATOR PASS → SHIP</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '0 4px' }}>
                  <svg viewBox="0 0 12 12" style={{ width: '10px', height: '10px', flex: 'none' }}><path d="M2 2l8 8M10 2l-8 8" fill="none" stroke="#8d8299" strokeWidth="1.5" strokeLinecap="round"></path></svg>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '7px', letterSpacing: '.06em', color: '#665073' }}>FAIL → TEMPLATE FALLBACK</span>
                </div>
              </div>
            )}
            {archStep === 5 && (
              <svg viewBox="0 0 180 140" style={{ width: '180px', height: '140px' }}>
                <rect x="24" y="20" width="132" height="100" rx="12" fill="#2a0a3d" stroke="rgba(233,182,255,0.12)" strokeWidth="1"></rect>
                <text x="90" y="40" fontFamily="IBM Plex Mono, monospace" fontSize="7" letterSpacing="0.06em" fill="#c65fe8" textAnchor="middle">AUDIT LOG</text>
                <line x1="40" y1="50" x2="140" y2="50" stroke="rgba(233,182,255,0.1)" strokeWidth="1"></line>
                <text x="46" y="64" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299">user_id</text>
                <text x="100" y="64" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#665073">user_001</text>
                <text x="46" y="76" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299">decision</text>
                <text x="100" y="76" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#e9b6ff">INTERVENE</text>
                <text x="46" y="88" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299">explanation</text>
                <text x="100" y="88" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#665073">"You have…"</text>
                <text x="46" y="100" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299">mode</text>
                <text x="100" y="100" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#665073">FIRE + FORGET</text>
                <text x="90" y="132" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#665073" textAnchor="middle">ERRORS DO NOT AFFECT VERDICT</text>
              </svg>
            )}
          </div>
        </div>

        <div style={{ marginTop: 'clamp(52px, 5.5vw, 80px)' }}>
          <div style={{ textAlign: 'center', marginBottom: 'clamp(28px, 3vw, 42px)' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.14em', textTransform: 'uppercase', color: '#c65fe8' }}>
              Deviation signals
            </span>
            <h3 style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '118%', fontSize: 'clamp(18px, 3.2vw, 38px)', letterSpacing: '-0.02em', textTransform: 'uppercase', color: '#e9d8f5', margin: '10px 0 0' }}>
              Four dimensions, eight signals
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 260px), 1fr))', gap: 'clamp(14px, 1.8vw, 22px)' }}>
            <div style={cardStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '108%', fontSize: '17px', textTransform: 'uppercase', color: '#f0e4f8' }}>Recipient</span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.08em', padding: '4px 9px', borderRadius: '999px', background: 'rgba(126,1,175,0.35)', color: '#e9b6ff' }}>STRUCTURAL</span>
              </div>
              <svg viewBox="0 0 200 60" style={{ width: '100%', height: 'auto' }}>
                <circle cx="40" cy="30" r="18" fill="#5c0f80"></circle>
                <circle cx="40" cy="30" r="10" fill="#7e01af"></circle>
                <circle cx="40" cy="30" r="4" fill="#e9b6ff"></circle>
                <line x1="58" y1="30" x2="82" y2="20" stroke="#c65fe8" strokeWidth="1" opacity="0.6"></line>
                <line x1="58" y1="30" x2="82" y2="40" stroke="#c65fe8" strokeWidth="1" opacity="0.6"></line>
                <circle cx="88" cy="20" r="6" fill="#4c0a69"></circle>
                <circle cx="88" cy="40" r="6" fill="#4c0a69"></circle>
                <line x1="94" y1="20" x2="118" y2="18" stroke="#665073" strokeWidth="1" strokeDasharray="2 2"></line>
                <circle cx="124" cy="18" r="5" fill="#3d0857"></circle>
                <text x="148" y="22" fontFamily="IBM Plex Mono, monospace" fontSize="7" fill="#8d8299">DIRECT</text>
                <text x="148" y="34" fontFamily="IBM Plex Mono, monospace" fontSize="7" fill="#665073">FOF</text>
                <text x="148" y="46" fontFamily="IBM Plex Mono, monospace" fontSize="7" fill="#4c0a69">NONE</text>
              </svg>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', color: '#c4b8cf' }}>recipient_familiarity <span style={{ color: '#665073' }}>float [0,1]</span></span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', color: '#c4b8cf' }}>graph_proximity <span style={{ color: '#665073' }}>float | None</span></span>
              </div>
              <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13px', lineHeight: 1.5, color: '#9a8ea6' }}>Recency-weighted, volume-floored. Capped at 0.2 if past volume is under 30% of the amount.</span>
            </div>

            <div style={cardStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '108%', fontSize: '17px', textTransform: 'uppercase', color: '#f0e4f8' }}>Amount</span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.08em', padding: '4px 9px', borderRadius: '999px', background: 'rgba(198,95,232,0.2)', color: '#c65fe8' }}>3 SIGNALS</span>
              </div>
              <svg viewBox="0 0 200 60" style={{ width: '100%', height: 'auto' }}>
                <path d="M10 50 C30 50 35 30 55 30 S80 45 100 45 S125 15 145 15 S170 40 190 40" fill="none" stroke="#c9a8dd" strokeWidth="1.5" strokeDasharray="3 3"></path>
                <path d="M10 48 C32 48 38 34 58 34 S82 42 102 42 S128 18 148 18 S172 38 190 38" fill="none" stroke="#7e01af" strokeWidth="2" strokeLinecap="round"></path>
                <circle cx="148" cy="18" r="5" fill="#c65fe8"></circle>
                <circle cx="148" cy="18" r="9" fill="none" stroke="#c65fe8" strokeWidth="1" opacity="0.5"></circle>
                <text x="148" y="8" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#e9b6ff" textAnchor="middle">Z-SCORE</text>
              </svg>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', color: '#c4b8cf' }}>amount_z_recipient <span style={{ color: '#665073' }}>float | None</span></span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', color: '#c4b8cf' }}>amount_z_global <span style={{ color: '#665073' }}>float</span></span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', color: '#c4b8cf' }}>amount_drift_ratio <span style={{ color: '#665073' }}>float | None</span></span>
              </div>
              <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13px', lineHeight: 1.5, color: '#9a8ea6' }}>Per-recipient and global z-scores. Drift ratio flags escalating amounts over 30d vs 90d windows.</span>
            </div>

            <div style={cardStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '108%', fontSize: '17px', textTransform: 'uppercase', color: '#f0e4f8' }}>Temporal</span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.08em', padding: '4px 9px', borderRadius: '999px', background: 'rgba(198,95,232,0.2)', color: '#c65fe8' }}>1 SIGNAL</span>
              </div>
              <svg viewBox="0 0 200 80" style={{ width: '100%', height: 'auto' }}>
                <circle cx="100" cy="40" r="32" fill="none" stroke="rgba(233,182,255,0.12)" strokeWidth="1"></circle>
                <circle cx="100" cy="40" r="22" fill="none" stroke="rgba(233,182,255,0.08)" strokeWidth="1"></circle>
                <line x1="100" y1="40" x2="100" y2="14" stroke="#7e01af" strokeWidth="2" strokeLinecap="round"></line>
                <line x1="100" y1="40" x2="124" y2="48" stroke="#c65fe8" strokeWidth="2" strokeLinecap="round"></line>
                <circle cx="100" cy="40" r="3" fill="#e9b6ff"></circle>
                <text x="100" y="8" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299" textAnchor="middle">12:00</text>
                <text x="140" y="43" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299">18:00</text>
                <text x="100" y="78" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#665073" textAnchor="middle">VON MISES</text>
              </svg>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', color: '#c4b8cf' }}>hour_deviation <span style={{ color: '#665073' }}>float [0,1]</span></span>
              </div>
              <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13px', lineHeight: 1.5, color: '#9a8ea6' }}>Circular-mean deviation using von Mises formula. 23:00 and 01:00 are treated as close.</span>
            </div>

            <div style={cardStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '108%', fontSize: '17px', textTransform: 'uppercase', color: '#f0e4f8' }}>Categorical</span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.08em', padding: '4px 9px', borderRadius: '999px', background: 'rgba(198,95,232,0.2)', color: '#c65fe8' }}>2 SIGNALS</span>
              </div>
              <svg viewBox="0 0 200 60" style={{ width: '100%', height: 'auto' }}>
                <rect x="10" y="8" width="84" height="44" rx="8" fill="rgba(126,1,175,0.2)" stroke="rgba(233,182,255,0.15)" strokeWidth="1"></rect>
                <text x="52" y="26" fontFamily="IBM Plex Mono, monospace" fontSize="9" fill="#e9b6ff" textAnchor="middle">NGN</text>
                <text x="52" y="40" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#8d8299" textAnchor="middle">FAMILIAR</text>
                <rect x="106" y="8" width="84" height="44" rx="8" fill="rgba(198,95,232,0.15)" stroke="#c65fe8" strokeWidth="1" strokeDasharray="4 3"></rect>
                <text x="148" y="26" fontFamily="IBM Plex Mono, monospace" fontSize="9" fill="#c65fe8" textAnchor="middle">USD</text>
                <text x="148" y="40" fontFamily="IBM Plex Mono, monospace" fontSize="6" fill="#c65fe8" textAnchor="middle">NOVEL</text>
              </svg>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', color: '#c4b8cf' }}>currency_novelty <span style={{ color: '#665073' }}>bool</span></span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', color: '#c4b8cf' }}>cross_border <span style={{ color: '#665073' }}>bool</span></span>
              </div>
              <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13px', lineHeight: 1.5, color: '#9a8ea6' }}>Boolean flags. Fires if the currency has never appeared or the transfer is cross-border.</span>
            </div>
          </div>
        </div>

        <div style={{ marginTop: 'clamp(52px, 5.5vw, 80px)' }}>
          <div style={{ textAlign: 'center', marginBottom: 'clamp(22px, 2.5vw, 34px)' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.14em', textTransform: 'uppercase', color: '#c65fe8' }}>
              Built with
            </span>
            <h3 style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '118%', fontSize: 'clamp(18px, 3.2vw, 38px)', letterSpacing: '-0.02em', textTransform: 'uppercase', color: '#e9d8f5', margin: '10px 0 0' }}>
              Tech stack
            </h3>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '10px', maxWidth: '900px', margin: '0 auto' }}>
            {techPills.map((tp, idx) => (
              <div key={idx} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 20px',
                borderRadius: '14px',
                background: 'rgba(42,10,61,0.5)',
                backdropFilter: 'blur(10px)',
                WebkitBackdropFilter: 'blur(10px)',
                border: '1px solid rgba(233,182,255,0.12)',
                transition: 'border-color .25s ease, transform .25s ease'
              }}>
                <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 800, fontSize: '13.5px', color: '#f0e4f8' }}>{tp.name}</span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.06em', color: '#8d8299' }}>{tp.ver}</span>
              </div>
            ))}
          </div>
          <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11.5px', letterSpacing: '.06em', color: '#665073', margin: '22px auto 0', textAlign: 'center' }}>
            PYTHON 3.11+ · FULLY TYPED · STRICT MYPY · 100% DETERMINISTIC SCORING
          </p>
        </div>
      </div>
    </section>
  );
}

const cardStyle = {
  background: 'rgba(42,10,61,0.55)',
  backdropFilter: 'blur(12px)',
  WebkitBackdropFilter: 'blur(12px)',
  border: '1px solid rgba(233,182,255,0.14)',
  borderRadius: '20px',
  padding: 'clamp(22px, 2.6vw, 32px)',
  display: 'flex',
  flexDirection: 'column',
  gap: '14px',
  transition: 'transform .3s ease, box-shadow .3s ease'
};
