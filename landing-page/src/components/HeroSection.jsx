import React from 'react';
import { HeroMascotEye } from './MascotEye';

export function HeroSection({ heroRef, mascotRefs }) {
  const { wrapRef, headRef, eyeRef, pupilRef, ringRef } = mascotRefs;

  return (
    <section ref={heroRef} data-screen-label="Hero" style={{
      position: 'relative',
      background: '#120a18',
      padding: 'clamp(48px, 7vw, 92px) clamp(18px, 5vw, 56px) clamp(56px, 7vw, 96px)',
      overflow: 'hidden'
    }}>
      {/* Shard 1 */}
      <div style={{ position: 'absolute', top: '12%', left: '6%', width: 'clamp(52px, 7vw, 96px)', transform: 'rotate(-16deg)', opacity: 0.85 }}>
        <div className="sentri-shard" style={{ animation: 'sentri-float 7.5s ease-in-out infinite' }}>
          <svg viewBox="0 0 100 140" style={{ width: '100%', height: 'auto', display: 'block' }}>
            <polygon points="50,4 88,52 62,136" fill="#8a1eb4"></polygon>
            <polygon points="50,4 62,136 30,120" fill="#5c0f80"></polygon>
            <polygon points="50,4 30,120 12,58" fill="#a044cc"></polygon>
          </svg>
        </div>
      </div>

      {/* Shard 2 */}
      <div style={{ position: 'absolute', top: '26%', right: '7%', width: 'clamp(44px, 6vw, 84px)', transform: 'rotate(22deg)', opacity: 0.8 }}>
        <div className="sentri-shard" style={{ animation: 'sentri-float 9s ease-in-out infinite', animationDelay: '-2.2s' }}>
          <svg viewBox="0 0 100 140" style={{ width: '100%', height: 'auto', display: 'block' }}>
            <polygon points="50,4 88,52 62,136" fill="#7e01af"></polygon>
            <polygon points="50,4 62,136 30,120" fill="#4c0a69"></polygon>
            <polygon points="50,4 30,120 12,58" fill="#9c3ac4"></polygon>
          </svg>
        </div>
      </div>

      {/* Shard 3 */}
      <div style={{ position: 'absolute', bottom: '20%', left: '11%', width: 'clamp(34px, 4.4vw, 62px)', transform: 'rotate(34deg)', opacity: 0.65 }}>
        <div className="sentri-shard" style={{ animation: 'sentri-float 8.2s ease-in-out infinite', animationDelay: '-4.5s' }}>
          <svg viewBox="0 0 100 140" style={{ width: '100%', height: 'auto', display: 'block' }}>
            <polygon points="50,4 88,52 62,136" fill="#660a8c"></polygon>
            <polygon points="50,4 62,136 30,120" fill="#3d0857"></polygon>
            <polygon points="50,4 30,120 12,58" fill="#8a1eb4"></polygon>
          </svg>
        </div>
      </div>

      {/* Shard 4 */}
      <div style={{ position: 'absolute', bottom: '26%', right: '13%', width: 'clamp(30px, 4vw, 54px)', transform: 'rotate(-28deg)', opacity: 0.6 }}>
        <div className="sentri-shard" style={{ animation: 'sentri-float 6.8s ease-in-out infinite', animationDelay: '-1.4s' }}>
          <svg viewBox="0 0 100 140" style={{ width: '100%', height: 'auto', display: 'block' }}>
            <polygon points="50,4 88,52 62,136" fill="#5c0f80"></polygon>
            <polygon points="50,4 62,136 30,120" fill="#340a49"></polygon>
            <polygon points="50,4 30,120 12,58" fill="#7e01af"></polygon>
          </svg>
        </div>
      </div>

      <div className="sentri-hero-in" style={{
        animation: 'sentri-hero-in 1s cubic-bezier(.16,.8,.24,1) both',
        position: 'relative',
        zIndex: 2,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center'
      }}>
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: '11.5px',
          letterSpacing: '.16em',
          color: '#c65fe8',
          textTransform: 'uppercase',
          marginBottom: 'clamp(20px, 3vw, 34px)'
        }}>Embedded security coprocessor for banking apps</span>

        <h1 style={{
          fontFamily: "'Archivo', sans-serif",
          fontWeight: 900,
          fontStretch: '125%',
          fontSize: 'clamp(26px, 8.6vw, 132px)',
          lineHeight: 0.85,
          letterSpacing: '-0.03em',
          textTransform: 'uppercase',
          color: '#e9d8f5',
          margin: 0
        }}>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>Fraud</span>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>that passes</span>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>every check</span>
        </h1>

        <HeroMascotEye
          wrapRef={wrapRef}
          headRef={headRef}
          eyeRef={eyeRef}
          pupilRef={pupilRef}
          ringRef={ringRef}
        />

        <p style={{
          fontFamily: "'IBM Plex Sans', sans-serif",
          fontSize: 'clamp(17.5px, 1.7vw, 20.5px)',
          lineHeight: 1.78,
          color: '#b9adc6',
          maxWidth: '65ch',
          margin: 'clamp(4px, 1.5vw, 14px) 0 0',
          textWrap: 'pretty'
        }}>
          Scam victims authorize their own transfers. Device, location, login and card all come back clean — so conventional fraud systems see nothing. Sentri learns how each customer actually moves money, and speaks up when a transfer doesn't fit.
        </p>

        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap', justifyContent: 'center', marginTop: '30px' }}>
          <a href="#how" style={{
            display: 'inline-block',
            fontFamily: "'Archivo', sans-serif",
            fontWeight: 900,
            fontStretch: '112%',
            fontSize: '15px',
            letterSpacing: '.03em',
            textTransform: 'uppercase',
            color: '#170320',
            background: '#f6eefb',
            padding: '19px 34px',
            borderRadius: '999px',
            transition: 'background 0.2s ease'
          }}>See how it works</a>

          <a href="#action" style={{
            display: 'inline-block',
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: '12px',
            letterSpacing: '.08em',
            textTransform: 'uppercase',
            color: '#c9bcd4',
            border: '1px solid rgba(233, 182, 255, 0.28)',
            padding: '18px 26px',
            borderRadius: '999px',
            transition: 'all 0.2s ease'
          }}>See the intervention</a>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
          gap: '0 26px',
          marginTop: 'clamp(34px, 4vw, 54px)',
          maxWidth: '660px',
          width: '100%'
        }}>
          <div style={{ padding: '16px 0 0', borderTop: '1px solid rgba(233,182,255,0.22)', display: 'flex', flexDirection: 'column', gap: '6px', textAlign: 'left' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.12em', color: '#8d8299', textTransform: 'uppercase' }}>Built for</span>
            <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13.5px', color: '#d6cbe0', lineHeight: 1.4 }}>Freelancers and cross-border earners</span>
          </div>
          <div style={{ padding: '16px 0 0', borderTop: '1px solid rgba(233,182,255,0.22)', display: 'flex', flexDirection: 'column', gap: '6px', textAlign: 'left' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.12em', color: '#8d8299', textTransform: 'uppercase' }}>Watches</span>
            <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13.5px', color: '#d6cbe0', lineHeight: 1.4 }}>Behavior, not devices</span>
          </div>
          <div style={{ padding: '16px 0 0', borderTop: '1px solid rgba(233,182,255,0.22)', display: 'flex', flexDirection: 'column', gap: '6px', textAlign: 'left' }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.12em', color: '#8d8299', textTransform: 'uppercase' }}>Never does</span>
            <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '13.5px', color: '#d6cbe0', lineHeight: 1.4 }}>Score, block or recommend</span>
          </div>
        </div>
      </div>
    </section>
  );
}
