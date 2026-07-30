import React, { useEffect, useState } from 'react';
import { WatcherMascotEye } from './MascotEye';

export function FloatingWatcher({ heroRef, mascotRefs }) {
  const [showWatcher, setShowWatcher] = useState(false);
  const { wrap2Ref, head2Ref, eye2Ref, pupil2Ref, ring2Ref } = mascotRefs;

  useEffect(() => {
    const handleScroll = () => {
      const hero = heroRef.current;
      const past = hero
        ? hero.getBoundingClientRect().bottom < window.innerHeight * 0.45
        : window.scrollY > window.innerHeight * 0.7;

      setShowWatcher(past);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [heroRef]);

  return (
    <div style={{
      position: 'fixed',
      right: '22px',
      bottom: '22px',
      zIndex: 55,
      width: '78px',
      opacity: showWatcher ? 1 : 0,
      transform: showWatcher ? 'translateY(0)' : 'translateY(18px)',
      transition: 'opacity .5s ease, transform .5s ease',
      pointerEvents: 'none'
    }}>
      <WatcherMascotEye
        wrap2Ref={wrap2Ref}
        head2Ref={head2Ref}
        eye2Ref={eye2Ref}
        pupil2Ref={pupil2Ref}
        ring2Ref={ring2Ref}
      />
    </div>
  );
}
