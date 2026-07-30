import React from 'react';

export function HeroMascotEye({ wrapRef, headRef, eyeRef, pupilRef, ringRef }) {
  return (
    <div ref={wrapRef} style={{
      position: 'relative',
      zIndex: 3,
      isolation: 'isolate',
      width: 'clamp(190px, 26vw, 330px)',
      marginTop: 'clamp(-28px, -2.6vw, -12px)'
    }}>
      <div style={{
        position: 'absolute',
        left: '50%',
        top: '46%',
        width: '150%',
        aspectRatio: '1',
        transform: 'translate(-50%, -50%)',
        background: 'radial-gradient(circle, rgba(198,95,200,0.15) 0%, rgba(198,95,200,0.06) 45%, rgba(198,95,200,0) 72%)',
        filter: 'blur(56px)',
        pointerEvents: 'none',
        zIndex: -1
      }}></div>

      <svg viewBox="0 0 400 420" style={{ width: '100%', height: 'auto', display: 'block', overflow: 'visible' }}>
        <defs>
          <radialGradient id="sg-glow-a" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#c65fe8" stopOpacity="0.42"></stop>
            <stop offset="100%" stopColor="#c65fe8" stopOpacity="0"></stop>
          </radialGradient>
          <radialGradient id="sg-eye-a" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#f2d5ff" stopOpacity="0.9"></stop>
            <stop offset="100%" stopColor="#7e01af" stopOpacity="0"></stop>
          </radialGradient>
          <clipPath id="sg-clip-a">
            <polygon points="200,140 230,148 252,170 260,200 252,230 230,252 200,260 170,252 148,230 140,200 148,170 170,148"></polygon>
          </clipPath>
        </defs>
        <ellipse cx="200" cy="200" rx="198" ry="190" fill="url(#sg-glow-a)"></ellipse>
        <ellipse cx="200" cy="374" rx="104" ry="12" fill="#3d0857" opacity="0.6"></ellipse>

        <g ref={headRef} style={{ transformBox: 'fill-box', transformOrigin: '50% 92%' }}>
          <polygon points="200,18 200,58 168,58" fill="#a044cc"></polygon>
          <polygon points="200,18 232,58 200,58" fill="#660a8c"></polygon>
          <polygon points="160,56 96,92 128,168 200,140 200,56" fill="#a044cc"></polygon>
          <polygon points="240,56 200,56 200,140 272,168 304,92" fill="#7e01af"></polygon>
          <polygon points="96,92 56,176 100,252 128,168" fill="#660a8c"></polygon>
          <polygon points="304,92 272,168 300,252 344,176" fill="#4c0a69"></polygon>
          <polygon points="56,176 82,288 140,306 100,252" fill="#5c0f80"></polygon>
          <polygon points="344,176 300,252 260,306 318,288" fill="#3d0857"></polygon>
          <polygon points="82,288 156,348 200,320 140,306" fill="#4c0a69"></polygon>
          <polygon points="318,288 244,348 200,320 260,306" fill="#2c0640"></polygon>
          <polygon points="140,306 200,320 260,306 230,268 170,268" fill="#5c0f80"></polygon>
          <polygon points="156,348 244,348 200,320" fill="#340a49"></polygon>
          <polyline points="200,18 168,58 96,92 56,176" fill="none" stroke="#d9a3f0" strokeWidth="2.5" opacity="0.4"></polyline>

          <g ref={eyeRef} class="sentri-eye" style={{ transformBox: 'fill-box', transformOrigin: 'center' }}>
            <polygon points="200,124 238,134.2 265.8,162 276,200 265.8,238 238,265.8 200,276 162,265.8 134.2,238 124,200 134.2,162 162,134.2" fill="#9c3ac4"></polygon>
            <polygon points="200,124 162,134.2 134.2,162 124,200 134.2,238 162,265.8 200,276 200,268 142,200 200,132" fill="#b45ad8" opacity="0.55"></polygon>
            <polygon points="200,140 230,148 252,170 260,200 252,230 230,252 200,260 170,252 148,230 140,200 148,170 170,148" fill="#150220"></polygon>
            <g clipPath="url(#sg-clip-a)">
              <circle cx="200" cy="200" r="50" fill="url(#sg-eye-a)"></circle>
              <g ref={pupilRef}>
                <circle cx="200" cy="200" r="32" fill="#c65fe8"></circle>
                <circle cx="200" cy="200" r="15" fill="#3f0a5c"></circle>
                <circle cx="188" cy="188" r="8" fill="#fbe9ff" opacity="0.95"></circle>
                <circle cx="211" cy="212" r="3.5" fill="#f2d5ff" opacity="0.6"></circle>
              </g>
              <rect className="sentri-eyelid" x="136" y="136" width="128" height="66" fill="#8a1eb4" style={{ transformBox: 'fill-box', transformOrigin: 'center top', transform: 'scaleY(0)' }}></rect>
            </g>
            <circle ref={ringRef} className="sentri-ring" cx="200" cy="200" r="86" fill="none" stroke="#e9b6ff" strokeWidth="3" opacity="0" style={{ transformBox: 'fill-box', transformOrigin: 'center' }}></circle>
          </g>
        </g>
      </svg>
    </div>
  );
}

export function WatcherMascotEye({ wrap2Ref, head2Ref, eye2Ref, pupil2Ref, ring2Ref }) {
  return (
    <div ref={wrap2Ref} style={{ position: 'relative', padding: '9px', borderRadius: '50%', background: 'rgba(18,10,24,0.72)', border: '1px solid rgba(233,182,255,0.22)', backdropFilter: 'blur(10px)', WebkitBackdropFilter: 'blur(10px)' }}>
      <svg viewBox="0 0 400 380" style={{ width: '100%', height: 'auto', display: 'block' }}>
        <defs>
          <radialGradient id="sg-eye-b" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#f2d5ff" stopOpacity="0.9"></stop>
            <stop offset="100%" stopColor="#7e01af" stopOpacity="0"></stop>
          </radialGradient>
          <clipPath id="sg-clip-b">
            <polygon points="200,140 230,148 252,170 260,200 252,230 230,252 200,260 170,252 148,230 140,200 148,170 170,148"></polygon>
          </clipPath>
        </defs>
        <g ref={head2Ref} style={{ transformBox: 'fill-box', transformOrigin: '50% 92%' }}>
          <polygon points="200,18 200,58 168,58" fill="#a044cc"></polygon>
          <polygon points="200,18 232,58 200,58" fill="#660a8c"></polygon>
          <polygon points="160,56 96,92 128,168 200,140 200,56" fill="#a044cc"></polygon>
          <polygon points="240,56 200,56 200,140 272,168 304,92" fill="#7e01af"></polygon>
          <polygon points="96,92 56,176 100,252 128,168" fill="#660a8c"></polygon>
          <polygon points="304,92 272,168 300,252 344,176" fill="#4c0a69"></polygon>
          <polygon points="56,176 82,288 140,306 100,252" fill="#5c0f80"></polygon>
          <polygon points="344,176 300,252 260,306 318,288" fill="#3d0857"></polygon>
          <polygon points="82,288 156,348 200,320 140,306" fill="#4c0a69"></polygon>
          <polygon points="318,288 244,348 200,320 260,306" fill="#2c0640"></polygon>
          <polygon points="140,306 200,320 260,306 230,268 170,268" fill="#5c0f80"></polygon>
          <polygon points="156,348 244,348 200,320" fill="#340a49"></polygon>
          <g ref={eye2Ref} className="sentri-eye" style={{ transformBox: 'fill-box', transformOrigin: 'center' }}>
            <polygon points="200,124 238,134.2 265.8,162 276,200 265.8,238 238,265.8 200,276 162,265.8 134.2,238 124,200 134.2,162 162,134.2" fill="#9c3ac4"></polygon>
            <polygon points="200,140 230,148 252,170 260,200 252,230 230,252 200,260 170,252 148,230 140,200 148,170 170,148" fill="#150220"></polygon>
            <g clipPath="url(#sg-clip-b)">
              <circle cx="200" cy="200" r="50" fill="url(#sg-eye-b)"></circle>
              <g ref={pupil2Ref}>
                <circle cx="200" cy="200" r="32" fill="#c65fe8"></circle>
                <circle cx="200" cy="200" r="15" fill="#3f0a5c"></circle>
                <circle cx="188" cy="188" r="8" fill="#fbe9ff" opacity="0.95"></circle>
              </g>
              <rect className="sentri-eyelid" x="136" y="136" width="128" height="66" fill="#8a1eb4" style={{ transformBox: 'fill-box', transformOrigin: 'center top', transform: 'scaleY(0)' }}></rect>
            </g>
            <circle ref={ring2Ref} className="sentri-ring" cx="200" cy="200" r="86" fill="none" stroke="#e9b6ff" strokeWidth="4" opacity="0" style={{ transformBox: 'fill-box', transformOrigin: 'center' }}></circle>
          </g>
        </g>
      </svg>
    </div>
  );
}
