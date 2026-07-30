import React from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';

export function CloseSection() {
  const [closeRef, , revealStyle] = useScrollReveal();

  return (
    <section data-screen-label="Close" ref={closeRef} style={{
      background: '#7e01af',
      padding: 'clamp(84px, 10vw, 140px) clamp(18px, 5vw, 56px) clamp(84px, 10vw, 140px)'
    }}>
      <div style={{ ...revealStyle, maxWidth: '1240px', margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '30px' }}>
        <h2 style={{
          fontFamily: "'Archivo', sans-serif",
          fontWeight: 900,
          fontStretch: '125%',
          fontSize: 'clamp(20px, 6.2vw, 90px)',
          lineHeight: 0.86,
          letterSpacing: '-0.03em',
          textTransform: 'uppercase',
          color: '#fdf7ff',
          margin: 0
        }}>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>Put Sentri</span>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>inside your app</span>
        </h2>
        <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '17px', lineHeight: 1.6, color: '#f4e4fb', margin: 0, maxWidth: '560px', textWrap: 'pretty' }}>
          The scam isn't going away. The blind spot can.
        </p>
        <button className="sentri-breathe" style={{
          fontFamily: "'Archivo', sans-serif",
          fontWeight: 900,
          fontStretch: '112%',
          fontSize: '15px',
          letterSpacing: '.03em',
          textTransform: 'uppercase',
          color: '#170320',
          background: '#f6eefb',
          padding: '20px 38px',
          borderRadius: '999px',
          border: 'none',
          cursor: 'pointer',
          transition: 'background 0.2s ease'
        }}>Get in touch</button>
      </div>
    </section>
  );
}
