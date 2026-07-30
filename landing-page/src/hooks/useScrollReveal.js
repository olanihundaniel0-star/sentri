import { useEffect, useState, useRef } from 'react';

export function useScrollReveal(threshold = 0.14) {
  const ref = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold }
    );

    observer.observe(el);

    return () => {
      if (el) observer.unobserve(el);
    };
  }, [threshold]);

  const revealStyle = {
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
    transition: 'opacity 0.9s cubic-bezier(0.16, 0.8, 0.24, 1), transform 0.9s cubic-bezier(0.16, 0.8, 0.24, 1)'
  };

  return [ref, isVisible, revealStyle];
}
