import React, { useState } from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';
import { IOSDevice } from './IOSDevice';

export function ActionSection() {
  const [actionRef, , revealStyle] = useScrollReveal();
  const [phoneFlagged, setPhoneFlagged] = useState(false);

  const typicalOn = !phoneFlagged;
  const btnBase = 'flex: 1; padding: 12px 10px; border-radius: 999px; font-family: "IBM Plex Mono", monospace; font-size: 10.5px; letter-spacing: .06em; cursor: pointer; transition: all .25s ease;';
  const typicalBtnStyle = typicalOn
    ? btnBase + ' border: 1px solid #7e01af; background: #7e01af; color: #fdf7ff;'
    : btnBase + ' border: 1px solid transparent; background: transparent; color: #a99bb5;';
  const flaggedBtnStyle = phoneFlagged
    ? btnBase + ' border: 1px solid #7e01af; background: #7e01af; color: #fdf7ff;'
    : btnBase + ' border: 1px solid transparent; background: transparent; color: #a99bb5;';

  return (
    <section id="action" data-screen-label="Sentri in action" ref={actionRef} style={{
      position: 'relative',
      background: '#120a18',
      padding: 'clamp(72px, 9vw, 128px) clamp(18px, 5vw, 56px)'
    }}>
      <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(233,182,255,0.05) 1px,transparent 1px),linear-gradient(90deg,rgba(233,182,255,0.05) 1px,transparent 1px)', backgroundSize: '64px 64px', pointerEvents: 'none' }}></div>

      <div style={{ ...revealStyle, position: 'relative', maxWidth: '1320px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.14em', textTransform: 'uppercase', color: '#c65fe8' }}>
            What the customer sees
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
            <span style={{ display: 'block', whiteSpace: 'nowrap' }}>Silent until</span>
            <span style={{ display: 'block', whiteSpace: 'nowrap' }}>it matters</span>
          </h2>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'clamp(30px, 4vw, 56px)', marginTop: 'clamp(38px, 4.5vw, 64px)' }}>
          <div style={{ flex: '0 0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ borderRadius: '48px', boxShadow: '0 0 0 1px rgba(233,182,255,0.22), 0 0 60px rgba(126,1,175,0.28), 0 40px 90px rgba(0,0,0,0.55)' }}>
              <IOSDevice dark width={320} height={700}>
                {!phoneFlagged ? (
                  <div style={{ minHeight: '100%', padding: '62px 22px 22px', display: 'flex', flexDirection: 'column', fontFamily: "'IBM Plex Sans', sans-serif", background: '#0f0e14' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '26px', color: 'rgba(255,255,255,0.55)' }}>
                      <svg viewBox="0 0 12 20" style={{ width: '8px', height: '14px', flex: 'none' }}>
                        <path d="M9 2L2 10l7 8" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                      </svg>
                      <span style={{ color: '#fff', fontSize: '15px', fontWeight: 500 }}>Transfer</span>
                    </div>

                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', textAlign: 'center' }}>
                      <div style={{ width: '54px', height: '54px', borderRadius: '50%', background: 'rgba(126,1,175,0.2)', border: '1px solid rgba(198,95,232,0.45)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#c65fe8' }}>
                        <svg viewBox="0 0 16 16" style={{ width: '22px', height: '22px' }}>
                          <path d="M3 8.5l3.2 3.2L13 5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                        </svg>
                      </div>
                      <div style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 800, fontSize: '21px', color: '#fff' }}>Transfer complete</div>
                      <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '26px', color: '#fff' }}>₦45,000</div>
                      <div style={{ fontSize: '13.5px', color: 'rgba(255,255,255,0.55)' }}>to Chidi O. · sent 14 times before</div>
                    </div>

                    <div style={{ textAlign: 'center', paddingTop: '16px' }}>
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '9.5px', letterSpacing: '.1em', color: 'rgba(255,255,255,0.55)' }}>
                        SENTRI CHECKED THIS · NOTHING TO SAY
                      </span>
                    </div>
                  </div>
                ) : (
                  <div style={{ minHeight: '100%', padding: '62px 22px 22px', display: 'flex', flexDirection: 'column', fontFamily: "'IBM Plex Sans', sans-serif", background: '#0f0e14' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', color: 'rgba(255,255,255,0.55)' }}>
                      <svg viewBox="0 0 12 20" style={{ width: '8px', height: '14px', flex: 'none' }}>
                        <path d="M9 2L2 10l7 8" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                      </svg>
                      <span style={{ color: '#fff', fontSize: '15px', fontWeight: 500 }}>Before you send</span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '18px' }}>
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '26px', color: '#fff' }}>₦280,000</span>
                      <span style={{ fontSize: '12.5px', color: 'rgba(255,255,255,0.55)' }}>to new recipient · 0801•••229</span>
                    </div>

                    <div style={{ background: 'rgba(126,1,175,0.16)', border: '1px solid rgba(198,95,232,0.4)', borderRadius: '16px', padding: '17px', display: 'flex', flexDirection: 'column', gap: '9px', marginBottom: 'auto' }}>
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '9.5px', letterSpacing: '.1em', color: '#e9b6ff' }}>WHAT IS DIFFERENT</span>
                      <span style={{ fontSize: '14px', lineHeight: 1.55, color: '#f6eefb' }}>You have not sent to this recipient before, and it is larger than your usual transfers this month.</span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '18px' }}>
                      <button style={{ padding: '14px', borderRadius: '999px', border: '1px solid rgba(255,255,255,0.24)', background: 'transparent', color: '#fff', fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '14px', fontWeight: 500, cursor: 'pointer' }}>
                        This is me — send anyway
                      </button>
                      <button style={{ padding: '14px', borderRadius: '999px', border: '1px solid rgba(255,255,255,0.24)', background: 'transparent', color: '#fff', fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '14px', fontWeight: 500, cursor: 'pointer' }}>
                        Stop, let me check
                      </button>
                    </div>

                    <div style={{ textAlign: 'center', paddingTop: '14px' }}>
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '9.5px', letterSpacing: '.1em', color: 'rgba(255,255,255,0.55)' }}>
                        NO SCORE · NO BLOCK · NO ADVICE
                      </span>
                    </div>
                  </div>
                )}
              </IOSDevice>
            </div>

            <div style={{ display: 'flex', gap: '8px', background: '#1b1222', border: '1px solid rgba(233,182,255,0.14)', borderRadius: '999px', padding: '6px', marginTop: '24px', width: '100%', maxWidth: '340px' }}>
              <button onClick={() => setPhoneFlagged(false)} style={{ ...parseInlineStyle(typicalBtnStyle) }}>TYPICAL TRANSFER</button>
              <button onClick={() => setPhoneFlagged(true)} style={{ ...parseInlineStyle(flaggedBtnStyle) }}>SOMETHING DIFFERENT</button>
            </div>
          </div>

          <div style={{ width: '100%', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 270px), 1fr))', gap: 'clamp(16px, 2vw, 26px)' }}>
            <div style={cardStyle('#2a0a3d')}>
              <h3 style={cardTitleStyle('#f0e4f8')}>It learns one customer's own normal</h3>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: '7px', height: '56px', alignSelf: 'flex-end' }}>
                <div style={{ width: '11px', height: '20px', background: '#4c0a69' }}></div>
                <div style={{ width: '11px', height: '38px', background: '#7e01af' }}></div>
                <div style={{ width: '11px', height: '28px', background: '#5c0f80' }}></div>
                <div style={{ width: '11px', height: '52px', background: '#c65fe8' }}></div>
                <div style={{ width: '11px', height: '32px', background: '#8a1eb4' }}></div>
              </div>
            </div>

            <div style={cardStyle('#ece2f5')}>
              <h3 style={cardTitleStyle('#2a0a3d')}>A transfer that fits stays silent</h3>
              <svg viewBox="0 0 120 80" style={{ width: '104px', height: '70px', alignSelf: 'flex-end' }}>
                <polygon points="60,6 110,32 110,66 60,74 10,66 10,32" fill="#d8c2e8"></polygon>
                <polygon points="60,6 110,32 60,44 10,32" fill="#efe6f7"></polygon>
                <circle cx="60" cy="46" r="7" fill="#7e01af"></circle>
              </svg>
            </div>

            <div style={cardStyle('#7e01af')}>
              <h3 style={cardTitleStyle('#fdf7ff')}>One that doesn't fit gets one plain sentence</h3>
              <div style={{ alignSelf: 'flex-end', width: '150px', padding: '15px 17px', background: '#2a0a3d', borderRadius: '14px 14px 14px 5px', display: 'flex', flexDirection: 'column', gap: '7px' }}>
                <div style={{ width: '84%', height: '6px', background: 'rgba(233,182,255,0.55)' }}></div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(233,182,255,0.55)' }}></div>
                <div style={{ width: '56%', height: '6px', background: 'rgba(233,182,255,0.55)' }}></div>
              </div>
            </div>

            <div style={cardStyle('#4a0f6b')}>
              <h3 style={cardTitleStyle('#f0e4f8')}>The customer decides, every time</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '9px', width: '100%', maxWidth: '190px', alignSelf: 'flex-end' }}>
                <div style={{ padding: '11px', borderRadius: '999px', border: '1.5px solid rgba(233,182,255,0.5)', textAlign: 'center', fontFamily: "'IBM Plex Mono', monospace", fontSize: '9.5px', letterSpacing: '.06em', color: '#e9b6ff' }}>SEND ANYWAY</div>
                <div style={{ padding: '11px', borderRadius: '999px', border: '1.5px solid rgba(233,182,255,0.5)', textAlign: 'center', fontFamily: "'IBM Plex Mono', monospace", fontSize: '9.5px', letterSpacing: '.06em', color: '#e9b6ff' }}>LET ME CHECK</div>
              </div>
            </div>
          </div>
        </div>

        <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13px', color: '#8d8299', margin: '26px auto 0', maxWidth: '480px', textAlign: 'center', textWrap: 'pretty' }}>
          Working mockup of the intervention screen. In production it renders inside the bank's own app UI, not a separate Sentri screen.
        </p>
      </div>
    </section>
  );
}

function parseInlineStyle(cssStr) {
  const obj = {};
  cssStr.split(';').forEach(rule => {
    const [key, val] = rule.split(':');
    if (key && val) {
      const camelKey = key.trim().replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      obj[camelKey] = val.trim();
    }
  });
  return obj;
}

function cardStyle(bg) {
  return {
    background: bg,
    borderRadius: '22px',
    padding: '26px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    gap: '24px',
    minHeight: '212px',
    transition: 'transform .3s ease-in-out, box-shadow .3s ease-in-out'
  };
}

function cardTitleStyle(color) {
  return {
    fontFamily: "'Archivo', sans-serif",
    fontWeight: 900,
    fontStretch: '108%',
    fontSize: 'clamp(19px, 1.9vw, 25px)',
    lineHeight: 1.15,
    color,
    margin: 0,
    textWrap: 'pretty'
  };
}
