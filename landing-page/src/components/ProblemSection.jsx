import React from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';

export function ProblemSection() {
  const [problemRef, isVisible, revealStyle] = useScrollReveal();

  const signalPills = [
    { label: 'DEVICE', check: true },
    { label: 'LOCATION', check: true },
    { label: 'LOGIN', check: true },
    { label: 'CARD', check: true },
    { label: 'THE PERSON — NOT CHECKED', check: false }
  ];

  return (
    <section id="problem" data-screen-label="Problem" ref={problemRef} style={{
      background: '#7e01af',
      padding: 'clamp(72px, 9vw, 128px) clamp(18px, 5vw, 56px)'
    }}>
      <div style={{ ...revealStyle, maxWidth: '1240px', margin: '0 auto' }}>
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '11px', letterSpacing: '.14em', textTransform: 'uppercase', color: '#efd6fb' }}>
          The case ordinary fraud detection cannot see
        </span>
        <h2 style={{
          fontFamily: "'Archivo', sans-serif",
          fontWeight: 900,
          fontStretch: '125%',
          fontSize: 'clamp(20px, 6.2vw, 82px)',
          lineHeight: 0.86,
          letterSpacing: '-0.03em',
          textTransform: 'uppercase',
          color: '#fdf7ff',
          margin: '14px 0 0'
        }}>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>Authorized</span>
          <span style={{ display: 'block', whiteSpace: 'nowrap' }}>by the victim</span>
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(280px, 0.9fr) minmax(320px, 1fr)',
          gap: 'clamp(32px, 4vw, 64px)',
          marginTop: 'clamp(38px, 4.5vw, 64px)',
          alignItems: 'start'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '17px', lineHeight: 1.62, color: '#f4e4fb', margin: 0, textWrap: 'pretty' }}>
              A fake recruiter on WhatsApp. A coached, urgent transfer. The account holder logs in from his own phone, types his own PIN, and sends the money himself. Nothing about it looks unauthorized — because nothing about it is.
            </p>
            <p style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '17px', lineHeight: 1.62, color: '#f4e4fb', margin: 0, textWrap: 'pretty' }}>
              Sentri is built for exactly this case: the person is the one being compromised, not the account.
            </p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '4px' }}>
              {signalPills.map((pill, i) => (
                <span key={i} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '7px',
                  padding: '9px 14px',
                  borderRadius: '999px',
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: '11.5px',
                  background: pill.check ? 'rgba(23, 3, 32, 0.28)' : '#170320',
                  color: pill.check ? '#f4e4fb' : '#e9b6ff',
                  opacity: isVisible ? 1 : 0,
                  transform: isVisible ? 'translateY(0)' : 'translateY(8px)',
                  transition: `opacity 0.5s ease ${(i * 0.11).toFixed(2)}s, transform 0.5s ease ${(i * 0.11).toFixed(2)}s`
                }}>
                  {pill.check && (
                    <svg viewBox="0 0 16 16" style={{ width: '12px', height: '12px', flex: 'none' }}>
                      <path d="M3 8.5l3.2 3.2L13 5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
                    </svg>
                  )}
                  {pill.label}
                </span>
              ))}
            </div>
            <p style={{
              fontFamily: "'Archivo', sans-serif",
              fontWeight: 800,
              fontStretch: '105%',
              fontSize: 'clamp(19px, 2.1vw, 26px)',
              lineHeight: 1.24,
              color: '#fdf7ff',
              margin: '12px 0 0',
              maxWidth: '460px',
              textWrap: 'pretty'
            }}>
              Every signal a bank already checks comes back clean. That is precisely why this scam works.
            </p>
          </div>

          <div style={{
            background: 'rgba(20, 20, 25, 0.7)',
            backdropFilter: 'blur(14px) saturate(140%)',
            WebkitBackdropFilter: 'blur(14px) saturate(140%)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '20px',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
            boxShadow: '0 24px 60px rgba(12, 4, 18, 0.4)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '11px', paddingBottom: '14px', borderBottom: '1px solid rgba(233, 182, 255, 0.1)' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'rgba(233, 182, 255, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Archivo', sans-serif", fontWeight: 800, fontSize: '14px', color: '#d6cbe0', flex: 'none' }}>G</div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '14px', fontWeight: 500, color: '#f3ecf7' }}>Grace · Meridian Talent Partners</span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10.5px', letterSpacing: '.06em', color: '#8d8299' }}>MESSAGING APP · UNVERIFIED</span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'flex-start' }}>
              <div style={{ maxWidth: '92%', background: 'rgba(233, 182, 255, 0.08)', borderRadius: '16px 16px 16px 5px', padding: '13px 16px', fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '14.5px', lineHeight: 1.5, color: '#e8e0ee' }}>
                Hello. This is Grace from Meridian Talent Partners. We reviewed your profile — remote data-entry role, $450 per week, flexible hours. Interested?
              </div>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.06em', color: '#8d8299', paddingLeft: '6px' }}>— READS LIKE A NORMAL RECRUITER</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <div style={{ maxWidth: '62%', background: 'rgba(126, 1, 175, 0.4)', borderRadius: '16px 16px 5px 16px', padding: '13px 16px', fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '14.5px', color: '#f3ecf7' }}>
                Yes, very interested.
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'flex-start' }}>
              <div style={{ maxWidth: '92%', background: 'rgba(233, 182, 255, 0.08)', borderRadius: '16px 16px 16px 5px', padding: '13px 16px', fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '14.5px', lineHeight: 1.5, color: '#e8e0ee' }}>
                Before onboarding, HR requires a refundable ₦45,000 verification deposit. It confirms you are a real applicant and is returned with your first paycheck.
              </div>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.06em', color: '#8d8299', paddingLeft: '6px' }}>— THE ASK, DRESSED UP AS ROUTINE</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'flex-start' }}>
              <div style={{ maxWidth: '92%', background: 'rgba(233, 182, 255, 0.08)', borderRadius: '16px 16px 16px 5px', padding: '13px 16px', fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '14.5px', lineHeight: 1.5, color: '#e8e0ee' }}>
                This batch closes today. Can you send it within the next 30 minutes?
              </div>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.06em', color: '#8d8299', paddingLeft: '6px' }}>— MANUFACTURED URGENCY</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'flex-end', marginTop: '2px' }}>
              <div style={{ maxWidth: '76%', background: '#7e01af', borderRadius: '16px 16px 5px 16px', padding: '13px 16px', fontFamily: "'IBM Plex Sans', sans-serif", fontSize: '14.5px', color: '#fff' }}>
                Transfer sent · ₦45,000
              </div>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: '10px', letterSpacing: '.06em', color: '#e9b6ff', paddingRight: '6px' }}>— HIS OWN PIN. EVERY SIGNAL CLEAN.</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
