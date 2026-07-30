import React, { useState } from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';

export function HowItWorksSection() {
  const [howRef, , revealStyle] = useScrollReveal();
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    { key: 'learn', n: '01', title: 'Learn', body: "Sentri builds a picture of one person's normal: who they pay, how much, how often, from where, on what kind of day. It is their own history, not a population average." },
    { key: 'compare', n: '02', title: 'Compare', body: "Every new transfer is checked against that picture — not a generic fraud model, not anyone else's behavior. A transfer that fits passes without a word." },
    { key: 'explain', n: '03', title: 'Explain', body: "A mismatch does not trigger a block. It triggers one short, factual sentence about what is different this time, in language a person reads in three seconds." },
    { key: 'decide', n: '04', title: 'You decide', body: "No score, no recommendation, no lecture. The customer reads the one fact that matters and chooses — with a few more seconds than the scammer wants them to have." }
  ];

  const active = steps[activeStep];

  return (
    <section id="how" data-screen-label="How Sentri works" ref={howRef} style={{
      background: 'linear-gradient(180deg, #7e01af 0%, #c07ad8 46px, #ddd0ea 118px, #ece2f5 240px)',
      padding: 'clamp(72px, 9vw, 128px) clamp(18px, 5vw, 56px)'
    }}>
      <div style={{ ...revealStyle, maxWidth: '1240px', margin: '0 auto' }}>
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.14em', textTransform: 'uppercase', color: '#7e01af' }}>
          The loop
        </span>
        <h2 style={{
          fontFamily: "'Archivo', sans-serif",
          fontWeight: 900,
          fontStretch: '125%',
          fontSize: 'clamp(20px, 6.2vw, 82px)',
          lineHeight: 0.86,
          letterSpacing: '-0.03em',
          textTransform: 'uppercase',
          color: '#2a0a3d',
          margin: '14px 0 0'
        }}>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>Compared to you,</span>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>not to everyone</span>
        </h2>
        <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '17px', lineHeight: 1.62, color: '#54405f', margin: '22px 0 0', maxWidth: '560px', textWrap: 'pretty' }}>
          Four steps run on every transfer. Most stop at step two, silently. Select a step to read it.
        </p>

        <div style={{ display: 'flex', justifyContent: 'flex-start', gap: 'clamp(16px, 3.4vw, 48px)', flexWrap: 'wrap', marginTop: 'clamp(34px, 4vw, 52px)' }}>
          {steps.map((step, i) => {
            const on = i === activeStep;
            return (
              <button
                key={step.key}
                onClick={() => setActiveStep(i)}
                style={{
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px',
                  padding: 0,
                  background: 'transparent',
                  border: 'none',
                  font: 'inherit',
                  textAlign: 'left'
                }}
              >
                <div style={on ? {
                  width: '54px', height: '54px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: '#7e01af', color: '#fdf7ff', fontFamily: "'IBM Plex Mono', monospace", fontSize: '13.5px',
                  transition: 'all .35s ease', boxShadow: '0 0 0 7px rgba(126,1,175,0.14)'
                } : {
                  width: '54px', height: '54px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: 'transparent', border: '1.5px solid rgba(42,10,61,0.24)', color: '#665073', fontFamily: "'IBM Plex Mono', monospace", fontSize: '13.5px',
                  transition: 'all .35s ease'
                }}>
                  {step.n}
                </div>
                <span style={on ? {
                  fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '110%', fontSize: '17px', letterSpacing: '.01em', textTransform: 'uppercase', color: '#2a0a3d', transition: 'color .3s ease'
                } : {
                  fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '110%', fontSize: '17px', letterSpacing: '.01em', textTransform: 'uppercase', color: '#6b5478', transition: 'color .3s ease'
                }}>
                  {step.title}
                </span>
              </button>
            );
          })}
        </div>

        <div style={{
          marginTop: '32px',
          background: '#fffdff',
          border: '1px solid rgba(42, 10, 61, 0.1)',
          borderRadius: '20px',
          padding: 'clamp(26px, 3.6vw, 44px)',
          display: 'grid',
          gridTemplateColumns: '1fr auto',
          gap: '32px',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '600px' }}>
            <h3 style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '110%', fontSize: 'clamp(22px, 2.4vw, 30px)', letterSpacing: '-0.01em', textTransform: 'uppercase', color: '#2a0a3d', margin: 0 }}>
              {active.title}
            </h3>
            <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '16px', lineHeight: 1.65, color: '#54405f', margin: 0, textWrap: 'pretty' }}>
              {active.body}
            </p>
          </div>

          <div style={{ width: '214px', height: '132px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {activeStep === 0 && (
              <svg viewBox="0 0 214 132" style={{ width: '214px', height: '132px' }}>
                <rect x="1" y="1" width="212" height="130" rx="10" fill="#f7f2fb" stroke="rgba(42,10,61,0.1)"></rect>
                <path d="M14 34H200M14 66H200M14 98H200" stroke="rgba(42,10,61,0.07)" strokeWidth="1"></path>
                <path d="M52 14V118M104 14V118M156 14V118" stroke="rgba(42,10,61,0.07)" strokeWidth="1"></path>
                <path d="M14 82C34 82 40 46 60 46S86 74 106 74s26-30 46-30 28 22 48 22" fill="none" stroke="#c9a8dd" strokeWidth="2" strokeDasharray="4 4"></path>
                <path d="M14 78C36 78 42 52 62 52s24 24 44 24 26-26 46-26 26 18 48 18" fill="none" stroke="#7e01af" strokeWidth="2.5" strokeLinecap="round"></path>
                <circle cx="30" cy="80" r="3" fill="#9c3ac4" opacity="0.55"></circle>
                <circle cx="46" cy="66" r="3" fill="#9c3ac4" opacity="0.55"></circle>
                <circle cx="58" cy="55" r="3.4" fill="#9c3ac4" opacity="0.7"></circle>
                <circle cx="74" cy="61" r="3" fill="#9c3ac4" opacity="0.55"></circle>
                <circle cx="92" cy="72" r="3.2" fill="#9c3ac4" opacity="0.6"></circle>
                <circle cx="110" cy="70" r="3" fill="#9c3ac4" opacity="0.5"></circle>
                <circle cx="128" cy="60" r="3.2" fill="#9c3ac4" opacity="0.6"></circle>
                <circle cx="146" cy="52" r="3" fill="#9c3ac4" opacity="0.5"></circle>
                <circle cx="164" cy="56" r="3.2" fill="#9c3ac4" opacity="0.6"></circle>
                <circle cx="182" cy="62" r="3" fill="#9c3ac4" opacity="0.5"></circle>
                <circle cx="120" cy="26" r="5" fill="#7e01af"></circle>
                <circle cx="120" cy="26" r="10" fill="none" stroke="#7e01af" strokeWidth="1.5" opacity="0.45"></circle>
                <circle cx="172" cy="108" r="4" fill="#7e01af" opacity="0.8"></circle>
                <text x="14" y="126" fontFamily="IBM Plex Mono, monospace" fontSize="7" letterSpacing="0.1em" fill="#665073">90 DAYS OF THIS PERSON</text>
              </svg>
            )}
            {activeStep === 1 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <svg viewBox="0 0 60 80" style={{ width: '44px', height: '60px' }}>
                  <polygon points="30,4 56,20 56,58 30,76 4,58 4,20" fill="#d8c2e8"></polygon>
                  <polygon points="30,4 56,20 30,36 4,20" fill="#e8dcf2"></polygon>
                </svg>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.1em', color: '#7e01af' }}>MATCH</span>
                <svg viewBox="0 0 60 80" style={{ width: '44px', height: '60px' }}>
                  <polygon points="30,4 56,20 56,58 30,76 4,58 4,20" fill="#7e01af"></polygon>
                  <polygon points="30,4 56,20 30,36 4,20" fill="#a044cc"></polygon>
                </svg>
              </div>
            )}
            {activeStep === 2 && (
              <div style={{ width: '154px', padding: '15px 17px', background: '#2a0a3d', borderRadius: '14px 14px 14px 5px', display: 'flex', flexDirection: 'column', gap: '7px' }}>
                <div style={{ width: '82%', height: '6px', background: 'rgba(233,182,255,0.6)' }}></div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(233,182,255,0.6)' }}></div>
                <div style={{ width: '58%', height: '6px', background: 'rgba(233,182,255,0.6)' }}></div>
              </div>
            )}
            {activeStep === 3 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '9px', width: '162px' }}>
                <div style={{ padding: '11px', borderRadius: '999px', border: '1.5px solid #7e01af', textAlign: 'center', fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.06em', color: '#4a0f6b' }}>SEND ANYWAY</div>
                <div style={{ padding: '11px', borderRadius: '999px', border: '1.5px solid #7e01af', textAlign: 'center', fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.06em', color: '#4a0f6b' }}>LET ME CHECK</div>
              </div>
            )}
          </div>
        </div>

        <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11.5px', letterSpacing: '.06em', color: '#665073', margin: '20px 0 0' }}>
          04 → 01 — EVERY DECISION, RIGHT OR WRONG, RETRAINS WHAT NORMAL MEANS.
        </p>
      </div>
    </section>
  );
}
