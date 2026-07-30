import React from 'react';

export function Header() {
  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 60,
      width: '100%',
      background: 'rgba(18, 10, 24, 0.78)',
      backdropFilter: 'blur(18px) saturate(150%)',
      WebkitBackdropFilter: 'blur(18px) saturate(150%)',
      borderBottom: '1px solid rgba(233, 182, 255, 0.1)'
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '14px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'relative'
      }}>
        {/* Left: Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <svg viewBox="0 0 24 24" style={{ width: '19px', height: '19px', flex: 'none' }}>
            <polygon points="12,2 22,7 22,17 12,22 2,17 2,7" fill="#7e01af"></polygon>
            <polygon points="12,2 22,7 12,12 2,7" fill="#a044cc"></polygon>
            <circle cx="12" cy="13" r="3" fill="#e9b6ff"></circle>
          </svg>
          <span style={{
            fontFamily: "'Archivo', sans-serif",
            fontWeight: 900,
            fontStretch: '115%',
            fontSize: '19px',
            letterSpacing: '-0.02em',
            color: '#f3ecf7'
          }}>SENTRI</span>
        </div>

        {/* Center: Nav Links */}
        <nav style={{
          position: 'absolute',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          alignItems: 'center',
          gap: '24px'
        }}>
          <a href="#problem" style={linkStyle}>PROBLEM</a>
          <a href="#how" style={linkStyle}>HOW IT WORKS</a>
          <a href="#action" style={linkStyle}>IN ACTION</a>
          <a href="#infra" style={linkStyle}>INFRASTRUCTURE</a>
          <a href="#arch" style={linkStyle}>ARCHITECTURE</a>
        </nav>

        {/* Right: CTA Button */}
        <div>
          <button style={{
            fontFamily: "'Archivo', sans-serif",
            fontWeight: 800,
            fontStretch: '110%',
            fontSize: '12.5px',
            letterSpacing: '.04em',
            padding: '12px 22px',
            borderRadius: '999px',
            background: '#f6eefb',
            color: '#170320',
            border: 'none',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            transition: 'background 0.2s ease, transform 0.15s ease'
          }}>GET IN TOUCH</button>
        </div>
      </div>
    </header>
  );
}

const linkStyle = {
  fontFamily: "'IBM Plex Mono', monospace",
  fontSize: '11px',
  letterSpacing: '.08em',
  color: '#a99bb5',
  textDecoration: 'none',
  transition: 'color 0.2s ease'
};
