import React from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';

export function CredibilitySection() {
  const [credRef, , revealStyle] = useScrollReveal();

  return (
    <section id="cred" data-screen-label="Credibility" ref={credRef} style={{
      background: '#ece2f5',
      padding: 'clamp(72px, 9vw, 128px) clamp(18px, 5vw, 56px)'
    }}>
      <div style={{ ...revealStyle, maxWidth: '800px', margin: '0 auto' }}>
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.14em', textTransform: 'uppercase', color: '#7e01af' }}>
          Where this stands
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
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>Built at</span>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>NITHUB 2026</span>
        </h2>
        <div style={{
          width: '100%',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '0 40px',
          marginTop: 'clamp(32px, 4vw, 52px)'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '7px', padding: '18px 2px', borderTop: '1px solid rgba(42, 10, 61, 0.16)' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.1em', color: '#665073', whiteSpace: 'nowrap' }}>EVENT</span>
            <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 700, fontSize: '17px', color: '#2a0a3d' }}>NITHUB Innovation Fair 2026</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '7px', padding: '18px 2px', borderTop: '1px solid rgba(42, 10, 61, 0.16)' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.1em', color: '#665073', whiteSpace: 'nowrap' }}>THEME</span>
            <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 700, fontSize: '17px', color: '#2a0a3d' }}>Intelligent Money for Everyone</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '7px', padding: '18px 2px', borderTop: '1px solid rgba(42, 10, 61, 0.16)' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.1em', color: '#665073', whiteSpace: 'nowrap' }}>ENGINE</span>
            <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 700, fontSize: '17px', color: '#2a0a3d' }}>Powered by BMONI</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '7px', padding: '18px 2px', borderTop: '1px solid rgba(42, 10, 61, 0.16)' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.1em', color: '#665073', whiteSpace: 'nowrap' }}>BUILT</span>
            <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 700, fontSize: '17px', color: '#2a0a3d' }}>Inside a single hackathon window — this page included</span>
          </div>
        </div>
      </div>
    </section>
  );
}
