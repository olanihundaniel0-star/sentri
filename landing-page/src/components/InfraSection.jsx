import React from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';

export function InfraSection() {
  const [infraRef, , revealStyle] = useScrollReveal();

  return (
    <section id="infra" data-screen-label="Why infrastructure" ref={infraRef} style={{
      background: '#2a0a3d',
      padding: 'clamp(72px, 9vw, 128px) clamp(18px, 5vw, 56px)'
    }}>
      <div style={{ ...revealStyle, maxWidth: '1240px', margin: '0 auto' }}>
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.14em', textTransform: 'uppercase', color: '#c65fe8' }}>
          How it ships
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
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>Infrastructure,</span>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>not an app</span>
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(300px, 1fr) minmax(280px, 0.85fr)',
          gap: 'clamp(32px, 4vw, 64px)',
          marginTop: 'clamp(38px, 4.5vw, 64px)',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', letterSpacing: '.12em', color: '#9a8ea6', marginBottom: '16px' }}>
              YOUR BANK'S APP
            </span>
            <div style={layerStyle(1, 'rgba(255,255,255,0.055)', 'rgba(255,255,255,0.12)')}>
              <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '15px', color: '#d6cbe0' }}>Login</span>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '9.5px', letterSpacing: '.08em', color: '#9a8ea6' }}>EXISTING</span>
            </div>
            <div style={{ ...layerStyle(2, 'rgba(255,255,255,0.055)', 'rgba(255,255,255,0.12)'), marginTop: '-10px' }}>
              <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '15px', color: '#d6cbe0' }}>Card controls</span>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '9.5px', letterSpacing: '.08em', color: '#9a8ea6' }}>EXISTING</span>
            </div>
            <div style={{ ...layerStyle(3, 'rgba(255,255,255,0.055)', 'rgba(255,255,255,0.12)'), marginTop: '-10px' }}>
              <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '15px', color: '#d6cbe0' }}>Transfers</span>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '9.5px', letterSpacing: '.08em', color: '#9a8ea6' }}>EXISTING</span>
            </div>
            <div style={{
              position: 'relative',
              zIndex: 4,
              marginTop: '-10px',
              background: 'rgba(126,1,175,0.42)',
              backdropFilter: 'blur(14px)',
              WebkitBackdropFilter: 'blur(14px)',
              border: '1px solid rgba(233,182,255,0.5)',
              borderRadius: '16px',
              padding: '22px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
              flexWrap: 'wrap',
              boxShadow: '0 0 44px rgba(126,1,175,0.6), 0 18px 40px rgba(8,2,14,0.45)'
            }}>
              <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '110%', fontSize: '16px', letterSpacing: '.02em', color: '#fdf7ff' }}>SENTRI</span>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '9.5px', letterSpacing: '.08em', color: '#f0d5fb' }}>FOUNDATION LAYER · CATCHES WHAT PASSES ABOVE</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '16.5px', lineHeight: 1.62, color: '#c4b8cf', margin: 0, textWrap: 'pretty' }}>
              Sentri sits inside a bank's existing app, between the confirm button and the ledger — checking the transfer being made right now against the pattern of everything that came before it.
            </p>
            <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '16.5px', lineHeight: 1.62, color: '#c4b8cf', margin: 0, textWrap: 'pretty' }}>
              Powered by BMONI, it runs as an embedded coprocessor: infrastructure a bank integrates once, not a feature its customers have to find.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0 22px', marginTop: '10px' }}>
              <div style={{ padding: '14px 0 0', borderTop: '1px solid rgba(233,182,255,0.22)', display: 'flex', flexDirection: 'column', gap: '7px' }}>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#c65fe8' }}>01</span>
                <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13.5px', color: '#d6cbe0' }}>No new app to download</span>
              </div>
              <div style={{ padding: '14px 0 0', borderTop: '1px solid rgba(233,182,255,0.22)', display: 'flex', flexDirection: 'column', gap: '7px' }}>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#c65fe8' }}>02</span>
                <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13.5px', color: '#d6cbe0' }}>No new login to create</span>
              </div>
              <div style={{ padding: '14px 0 0', borderTop: '1px solid rgba(233,182,255,0.22)', display: 'flex', flexDirection: 'column', gap: '7px' }}>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', color: '#c65fe8' }}>03</span>
                <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13.5px', color: '#d6cbe0' }}>No habit to change</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function layerStyle(zIndex, bg, border) {
  return {
    position: 'relative',
    zIndex,
    background: bg,
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
    border: `1px solid ${border}`,
    borderRadius: '16px',
    padding: '19px 22px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '12px',
    boxShadow: '0 14px 30px rgba(8,2,14,0.35)'
  };
}
