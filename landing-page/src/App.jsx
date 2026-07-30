import React, { useRef, useEffect } from 'react';
import { Header } from './components/Header';
import { HeroSection } from './components/HeroSection';
import { ProblemSection } from './components/ProblemSection';
import { HowItWorksSection } from './components/HowItWorksSection';
import { ActionSection } from './components/ActionSection';
import { InfraSection } from './components/InfraSection';
import { ArchitectureSection } from './components/ArchitectureSection';
import { CredibilitySection } from './components/CredibilitySection';
import { CloseSection } from './components/CloseSection';
import { Footer } from './components/Footer';
import { FloatingWatcher } from './components/FloatingWatcher';
import { useMouseMascot } from './hooks/useMouseMascot';

export function App() {
  const heroRef = useRef(null);
  const mascotRefs = useMouseMascot({ mascotStartleEnabled: true });

  useEffect(() => {
    if (window.location.hash) {
      const el = document.querySelector(window.location.hash);
      if (el) {
        setTimeout(() => el.scrollIntoView({ behavior: 'instant', block: 'start' }), 100);
      }
    }
  }, []);

  return (
    <div style={{ background: '#120a18', overflowX: 'clip', minHeight: '100vh' }}>
      <Header />
      <main>
        <HeroSection heroRef={heroRef} mascotRefs={mascotRefs} />
        <ProblemSection />
        <HowItWorksSection />
        <ActionSection />
        <InfraSection />
        <ArchitectureSection />
        <CredibilitySection />
        <CloseSection />
      </main>
      <Footer />
      <FloatingWatcher heroRef={heroRef} mascotRefs={mascotRefs} />
    </div>
  );
}

export default App;
