import { useEffect, useRef } from 'react';

export function useMouseMascot({ mascotStartleEnabled = true } = {}) {
  const wrapRef = useRef(null);
  const headRef = useRef(null);
  const pupilRef = useRef(null);
  const ringRef = useRef(null);
  const eyeRef = useRef(null);

  const wrap2Ref = useRef(null);
  const head2Ref = useRef(null);
  const pupil2Ref = useRef(null);
  const ring2Ref = useRef(null);
  const eye2Ref = useRef(null);

  useEffect(() => {
    const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) return;

    let rectA = null;
    let rectB = null;

    const measure = () => {
      if (wrapRef.current) rectA = wrapRef.current.getBoundingClientRect();
      if (wrap2Ref.current) rectB = wrap2Ref.current.getBoundingClientRect();
    };

    measure();

    const aimAt = (rect, e) => {
      if (!rect) return { x: 0, y: 0 };
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;
      const dist = Math.hypot(dx, dy) || 1;
      const mag = Math.min(dist / 300, 1);
      return { x: (dx / dist) * mag, y: (dy / dist) * mag };
    };

    let targetA = { x: 0, y: 0 };
    let curA = { x: 0, y: 0 };
    let targetB = { x: 0, y: 0 };
    let curB = { x: 0, y: 0 };
    let lastMove = null;
    const speeds = [];
    let lastStartle = 0;
    let startleKick = 0;

    const triggerStartle = () => {
      [ringRef.current, ring2Ref.current].forEach((ring) => {
        if (!ring) return;
        ring.classList.remove('is-pulsing');
        void ring.getBoundingClientRect();
        ring.classList.add('is-pulsing');
      });
      [eyeRef.current, eye2Ref.current].forEach((eye) => {
        if (!eye) return;
        eye.classList.add('is-startled');
        setTimeout(() => eye.classList.remove('is-startled'), 210);
      });
    };

    const handleMouseMove = (e) => {
      targetA = aimAt(rectA, e);
      targetB = aimAt(rectB, e);

      const now = performance.now();
      if (lastMove) {
        const dt = now - lastMove.t;
        if (dt > 0) {
          const speed = Math.hypot(e.clientX - lastMove.x, e.clientY - lastMove.y) / dt;
          speeds.push(speed);
          if (speeds.length > 8) speeds.shift();
          const avg = speeds.reduce((a, b) => a + b, 0) / speeds.length;

          if (mascotStartleEnabled && speed > 2.2 && speed > avg * 2.8 && speeds.length >= 4 && now - lastStartle > 1600) {
            lastStartle = now;
            startleKick = targetA.x >= 0 ? -6 : 6;
            triggerStartle();
          }
        }
      }
      lastMove = { x: e.clientX, y: e.clientY, t: now };
    };

    let rafId = null;

    const tick = () => {
      curA.x += (targetA.x - curA.x) * 0.13;
      curA.y += (targetA.y - curA.y) * 0.13;
      curB.x += (targetB.x - curB.x) * 0.13;
      curB.y += (targetB.y - curB.y) * 0.13;

      startleKick *= 0.82;
      if (Math.abs(startleKick) < 0.05) startleKick = 0;

      if (pupilRef.current) {
        pupilRef.current.style.transform = `translate(${(curA.x * 16).toFixed(2)}px, ${(curA.y * 14).toFixed(2)}px)`;
      }
      if (headRef.current) {
        headRef.current.style.transform = `rotate(${(curA.x * 2.4 + startleKick).toFixed(2)}deg)`;
      }

      if (pupil2Ref.current) {
        pupil2Ref.current.style.transform = `translate(${(curB.x * 16).toFixed(2)}px, ${(curB.y * 14).toFixed(2)}px)`;
      }
      if (head2Ref.current) {
        head2Ref.current.style.transform = `rotate(${(curB.x * 2.4 + startleKick).toFixed(2)}deg)`;
      }

      rafId = requestAnimationFrame(tick);
    };

    const handleScrollOrResize = () => {
      measure();
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('scroll', handleScrollOrResize, { passive: true });
    window.addEventListener('resize', handleScrollOrResize);
    rafId = requestAnimationFrame(tick);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', handleScrollOrResize);
      window.removeEventListener('resize', handleScrollOrResize);
      if (rafId) cancelAnimationFrame(rafId);
    };
  }, [mascotStartleEnabled]);

  return {
    wrapRef, headRef, pupilRef, ringRef, eyeRef,
    wrap2Ref, head2Ref, pupil2Ref, ring2Ref, eye2Ref
  };
}
