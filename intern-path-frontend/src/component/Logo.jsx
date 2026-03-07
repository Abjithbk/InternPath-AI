import React from 'react';

/**
 * Internpath Logo Component
 * * Usage:
 * <Logo width={200} />
 */
const Logo = ({ width = 150, className = "", showText = true }) => {
  return (
    <div className={`flex flex-col items-center justify-center leading-none shrink-0 ${className}`}>
      <svg 
        width={width} 
        viewBox="0 0 100 100" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        className="block"
      >
        {/* Dark Blue Elements (Navy) */}
        <g fill="#0a1930">
          <polygon points="50,15 72,25 50,35 28,25" />
          <circle cx="50" cy="42" r="9" />
          <path d="M 18 46 Q 35 60 50 88 Q 65 60 82 46 Q 70 52 56 48 L 50 58 L 44 48 Q 30 52 18 46 Z" />
        </g>
        
        {/* Light Blue Elements (Primary Blue) */}
        <g fill="#3b82f6">
          <path d="M 12 50 Q 35 65 50 95 Q 65 65 88 50 Q 65 72 50 85 Q 35 72 12 50 Z" />
          <path d="M 50 15 Q 32 18 32 35" fill="none" stroke="#0a1930" strokeWidth="2" />
          <circle cx="32" cy="35" r="2.5" />
          <polygon points="30,35 34,35 35,43 29,43" />
        </g>
      </svg>

      {showText && (
        <span style={{ 
          fontFamily: 'sans-serif', 
          fontWeight: '900', 
          fontSize: `${width * 0.15}px`,
          color: '#0a1930',
          textShadow: `-1px 1px 0px #3b82f6`,
          marginTop: '8px',
          letterSpacing: '1px'
        }}>
          INTERNPATH
        </span>
      )}
    </div>
  );
};

export default Logo;