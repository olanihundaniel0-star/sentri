import React, { useState } from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';

export function ArchitectureSection() {
  const [archRef, , revealStyle] = useScrollReveal();
  const [archStep, setArchStep] = useState(0);

  const archStepsData = [
    { key: 'fetch', n: '①', title: 'Fetch', icon: '⬇', body: "Pull the user's full transaction history and social graph from BMONI via the BMONIClient. Two implementations: an in-memory stub backed by seed data for development, or the real BMONI sandbox adapter using standard fetch with x-api-key auth.", tags: ['protocol.js', 'stub.js', 'client.js'] },
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
            <span style={{ display: 'block', whiteSpace: 'nowrap' }}>The Evaluation</span>
            <span style={{ display: 'block', whiteSpace: 'nowrap' }}>Pipeline</span>
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
          gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 340px), 1fr))',
          gap: '36px',
          alignItems: 'center',
          boxShadow: '0 24px 60px rgba(8,2,14,0.5)'
        }}>
          {/* Left Column: 50% Text */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.1em', color: '#c65fe8' }}>{active.n}</span>
              <h3 style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '110%', fontSize: 'clamp(22px, 2.4vw, 30px)', letterSpacing: '-0.01em', textTransform: 'uppercase', color: '#f0e4f8', margin: 0 }}>{active.title}</h3>
            </div>
            <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '16px', lineHeight: 1.65, color: '#c4b8cf', margin: 0, textWrap: 'pretty' }}>{active.body}</p>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
              {active.tags.map((tag, idx) => (
                <span key={idx} style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.08em', padding: '6px 12px', borderRadius: '999px', background: 'rgba(126,1,175,0.3)', border: '1px solid rgba(233,182,255,0.2)', color: '#e9b6ff' }}>
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Right Column: 50% Glassmorphic Diagram */}
          <div style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {archStep === 0 && (
              <div style={{
                width: '100%',
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                padding: '20px',
                background: 'rgba(20, 9, 32, 0.7)',
                border: '1px solid rgba(233, 182, 255, 0.18)',
                borderRadius: '16px',
                backdropFilter: 'blur(16px)',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
                  <div style={{
                    flex: 1,
                    padding: '16px 14px',
                    background: 'rgba(42, 10, 61, 0.8)',
                    border: '1px solid rgba(198, 95, 232, 0.4)',
                    borderRadius: '12px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '4px',
                    boxShadow: '0 4px 16px rgba(126, 1, 175, 0.2)'
                  }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '13px', fontWeight: 700, letterSpacing: '.08em', color: '#c65fe8' }}>BMONI</span>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#a99bb5', textAlign: 'center' }}>WALLET ENGINE</span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', fontWeight: 600, color: '#c65fe8', letterSpacing: '.06em' }}>x-api-key</span>
                    <div style={{ width: '54px', height: '0', borderTop: '2px dashed #c65fe8' }}></div>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', color: '#8d8299' }}>fetch()</span>
                  </div>

                  <div style={{
                    flex: 1,
                    padding: '16px 14px',
                    background: 'rgba(126, 1, 175, 0.3)',
                    border: '1px solid rgba(233, 182, 255, 0.5)',
                    borderRadius: '12px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '4px',
                    boxShadow: '0 4px 20px rgba(126, 1, 175, 0.3)'
                  }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '13px', fontWeight: 700, letterSpacing: '.08em', color: '#e9b6ff' }}>SENTRI</span>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#f0e4f8', textAlign: 'center' }}>COPROCESSOR</span>
                  </div>
                </div>

                <div style={{
                  width: '100%',
                  padding: '14px',
                  background: 'rgba(30, 10, 48, 0.7)',
                  border: '1.5px dashed rgba(233, 182, 255, 0.25)',
                  borderRadius: '12px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '4px',
                  textAlign: 'center'
                }}>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px', fontWeight: 600, color: '#e9b6ff', letterSpacing: '.04em' }}>TRANSACTION HISTORY</span>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#b9adc6' }}>+ SOCIAL GRAPH DATA</span>
                </div>
              </div>
            )}

            {archStep === 1 && (
              <div style={{
                width: '100%',
                padding: '20px',
                background: 'rgba(20, 9, 32, 0.7)',
                border: '1px solid rgba(233, 182, 255, 0.18)',
                borderRadius: '16px',
                backdropFilter: 'blur(16px)',
                display: 'flex',
                flexDirection: 'column',
                gap: '14px'
              }}>
                <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#c65fe8', letterSpacing: '.06em', textAlign: 'center' }}>
                  USER PROFILE AGGREGATION
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div style={{ background: 'rgba(42, 10, 61, 0.6)', border: '1px solid rgba(233, 182, 255, 0.15)', borderRadius: '10px', padding: '12px' }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#8d8299', display: 'block', marginBottom: '6px' }}>RECIPIENT ROLLUPS</span>
                    <div style={{ width: '100%', height: '8px', background: '#7e01af', borderRadius: '4px', marginBottom: '4px' }}></div>
                    <div style={{ width: '65%', height: '8px', background: '#4c0a69', borderRadius: '4px' }}></div>
                  </div>
                  <div style={{ background: 'rgba(42, 10, 61, 0.6)', border: '1px solid rgba(233, 182, 255, 0.15)', borderRadius: '10px', padding: '12px' }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#8d8299', display: 'block', marginBottom: '6px' }}>CURRENCIES</span>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#e9b6ff' }}>NGN</span>
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#665073' }}>USD</span>
                    </div>
                  </div>
                </div>
                <div style={{ background: 'rgba(42, 10, 61, 0.6)', border: '1px solid rgba(233, 182, 255, 0.15)', borderRadius: '10px', padding: '12px' }}>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#8d8299', display: 'block', marginBottom: '8px' }}>24-HOUR HISTOGRAM</span>
                  <div style={{ display: 'flex', alignItems: 'flex-end', gap: '6px', height: '36px' }}>
                    <div style={{ flex: 1, height: '40%', background: '#5c0f80', borderRadius: '2px' }}></div>
                    <div style={{ flex: 1, height: '60%', background: '#5c0f80', borderRadius: '2px' }}></div>
                    <div style={{ flex: 1, height: '100%', background: '#7e01af', borderRadius: '2px' }}></div>
                    <div style={{ flex: 1, height: '70%', background: '#5c0f80', borderRadius: '2px' }}></div>
                    <div style={{ flex: 1, height: '30%', background: '#4c0a69', borderRadius: '2px' }}></div>
                    <div style={{ flex: 1, height: '20%', background: '#3d0857', borderRadius: '2px' }}></div>
                  </div>
                </div>
              </div>
            )}

            {archStep === 2 && (
              <div style={{
                width: '100%',
                padding: '20px',
                background: 'rgba(20, 9, 32, 0.7)',
                border: '1px solid rgba(233, 182, 255, 0.18)',
                borderRadius: '16px',
                backdropFilter: 'blur(16px)',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}>
                <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#c65fe8', letterSpacing: '.06em', textAlign: 'center' }}>
                  DEVIATION VECTOR (8 SIGNALS)
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div style={{ background: 'rgba(126, 1, 175, 0.25)', border: '1px solid rgba(233, 182, 255, 0.2)', borderRadius: '10px', padding: '10px 12px', textAlign: 'center' }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#e9b6ff', display: 'block' }}>RECIPIENT</span>
                    <span style={{ fontFamily: "'Archivo', sans-serif", fontSize: '16px', fontWeight: 900, color: '#f0e4f8' }}>2 SIGNALS</span>
                  </div>
                  <div style={{ background: 'rgba(126, 1, 175, 0.25)', border: '1px solid rgba(233, 182, 255, 0.2)', borderRadius: '10px', padding: '10px 12px', textAlign: 'center' }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#e9b6ff', display: 'block' }}>AMOUNT</span>
                    <span style={{ fontFamily: "'Archivo', sans-serif", fontSize: '16px', fontWeight: 900, color: '#f0e4f8' }}>3 SIGNALS</span>
                  </div>
                  <div style={{ background: 'rgba(126, 1, 175, 0.25)', border: '1px solid rgba(233, 182, 255, 0.2)', borderRadius: '10px', padding: '10px 12px', textAlign: 'center' }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#e9b6ff', display: 'block' }}>TEMPORAL</span>
                    <span style={{ fontFamily: "'Archivo', sans-serif", fontSize: '16px', fontWeight: 900, color: '#f0e4f8' }}>1 SIGNAL</span>
                  </div>
                  <div style={{ background: 'rgba(126, 1, 175, 0.25)', border: '1px solid rgba(233, 182, 255, 0.2)', borderRadius: '10px', padding: '10px 12px', textAlign: 'center' }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#e9b6ff', display: 'block' }}>CATEGORICAL</span>
                    <span style={{ fontFamily: "'Archivo', sans-serif", fontSize: '16px', fontWeight: 900, color: '#f0e4f8' }}>2 SIGNALS</span>
                  </div>
                </div>
              </div>
            )}

            {archStep === 3 && (
              <div style={{
                width: '100%',
                padding: '20px',
                background: 'rgba(20, 9, 32, 0.7)',
                border: '1px solid rgba(233, 182, 255, 0.18)',
                borderRadius: '16px',
                backdropFilter: 'blur(16px)',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                textAlign: 'center'
              }}>
                <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#c65fe8', letterSpacing: '.06em' }}>
                  THRESHOLD EVALUATION
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ padding: '10px 14px', background: 'rgba(42, 10, 61, 0.6)', border: '1px solid rgba(233, 182, 255, 0.15)', borderRadius: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px', color: '#8d8299' }}>STRUCTURAL ONLY</span>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px', fontWeight: 700, color: '#8d8299' }}>SILENT_PASS</span>
                  </div>
                  <div style={{ padding: '10px 14px', background: 'rgba(126, 1, 175, 0.3)', border: '1px solid rgba(198, 95, 232, 0.4)', borderRadius: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px', color: '#f0e4f8' }}>NON-STRUCTURAL FIRED</span>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px', fontWeight: 700, color: '#e9b6ff' }}>INTERVENE</span>
                  </div>
                </div>
              </div>
            )}

            {archStep === 4 && (
              <div style={{
                width: '100%',
                padding: '20px',
                background: 'rgba(20, 9, 32, 0.7)',
                border: '1px solid rgba(233, 182, 255, 0.18)',
                borderRadius: '16px',
                backdropFilter: 'blur(16px)',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}>
                <div style={{ padding: '12px 14px', background: '#2a0a3d', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px', fontWeight: 700, color: '#c65fe8' }}>CLAUDE SYNTHESIZER</span>
                  <div style={{ width: '90%', height: '4px', background: 'rgba(233,182,255,0.4)', borderRadius: '2px' }}></div>
                  <div style={{ width: '100%', height: '4px', background: 'rgba(233,182,255,0.4)', borderRadius: '2px' }}></div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px', color: '#c65fe8' }}>✓ VALIDATOR PASS → SHIP EXPLANATION</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px', color: '#8d8299' }}>✕ FAIL → TEMPLATE FALLBACK</span>
                </div>
              </div>
            )}

            {archStep === 5 && (
              <div style={{
                width: '100%',
                padding: '20px',
                background: 'rgba(20, 9, 32, 0.7)',
                border: '1px solid rgba(233, 182, 255, 0.18)',
                borderRadius: '16px',
                backdropFilter: 'blur(16px)',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '13px', fontWeight: 700, color: '#c65fe8', textAlign: 'center', marginBottom: '4px' }}>FIRE-AND-FORGET AUDIT LOG</span>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px' }}>
                  <span style={{ color: '#8d8299' }}>user_id</span>
                  <span style={{ color: '#f0e4f8' }}>user_001</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px' }}>
                  <span style={{ color: '#8d8299' }}>decision</span>
                  <span style={{ color: '#e9b6ff', fontWeight: 700 }}>INTERVENE</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: "'IBM Plex Mono', monospace", fontSize: '12px' }}>
                  <span style={{ color: '#8d8299' }}>explanation</span>
                  <span style={{ color: '#c4b8cf' }}>"You have not sent..."</span>
                </div>
                <div style={{ textAlign: 'center', marginTop: '8px', fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#665073' }}>
                  ERRORS DO NOT AFFECT VERDICT
                </div>
              </div>
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
