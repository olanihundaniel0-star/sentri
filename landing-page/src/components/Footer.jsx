import React from 'react';

export function Footer() {
  return (
    <footer style={{ background: '#120a18', padding: '44px clamp(18px, 5vw, 56px)' }}>
      <div style={{ maxWidth: '1240px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '24px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
            <svg viewBox="0 0 24 24" style={{ width: '16px', height: '16px', flex: 'none' }}>
              <polygon points="12,2 22,7 22,17 12,22 2,17 2,7" fill="#7e01af"></polygon>
              <polygon points="12,2 22,7 12,12 2,7" fill="#a044cc"></polygon>
              <circle cx="12" cy="13" r="3" fill="#e9b6ff"></circle>
            </svg>
            <span style={{ fontFamily: "'Archivo', sans-serif", fontWeight: 900, fontStretch: '112%', fontSize: '15px', color: '#f3ecf7' }}>SENTRI</span>
          </div>
          <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13px', color: '#8d8299', maxWidth: '340px', lineHeight: 1.5 }}>
            An embedded AI security coprocessor for banking apps.
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end', textAlign: 'right' }}>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', letterSpacing: '.1em', color: '#8d8299' }}>NITHUB INNOVATION FAIR · 2026</span>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', letterSpacing: '.1em', color: '#8d8299' }}>POWERED BY BMONI</span>
        </div>
      </div>
    </footer>
  );
}
