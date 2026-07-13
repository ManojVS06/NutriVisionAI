import React from 'react';

export function CalorieRing({ consumed, target }) {
  const percentage = Math.min(100, Math.round((consumed / (target || 1)) * 100));
  
  // SVG Circle geometry
  const radius = 70;
  const strokeWidth = 12;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', padding: '30px' }}>
      <div style={{ position: 'relative', width: '160px', height: '160px' }}>
        <svg width="100%" height="100%" viewBox="0 0 160 160" style={{ transform: 'rotate(-90deg)', overflow: 'visible' }}>
          {/* Track Ring */}
          <circle 
            cx="80" 
            cy="80" 
            r={radius} 
            fill="none" 
            stroke="rgba(255,255,255,0.04)" 
            strokeWidth={strokeWidth} 
          />
          {/* Active Ring */}
          <circle 
            cx="80" 
            cy="80" 
            r={radius} 
            fill="none" 
            stroke="url(#calorieGrad)" 
            strokeWidth={strokeWidth} 
            strokeDasharray={circumference} 
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{ filter: 'drop-shadow(0px 0px 8px rgba(139, 92, 246, 0.4))' }}
          />
          {/* Define Gradient */}
          <defs>
            <linearGradient id="calorieGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="var(--color-purple)" />
              <stop offset="100%" stopColor="var(--color-indigo)" />
            </linearGradient>
          </defs>
        </svg>
        
        {/* Core Value Label Overlay */}
        <div style={{ 
          position: 'absolute', 
          top: 0, 
          left: 0, 
          width: '100%', 
          height: '100%', 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center' 
        }}>
          <span style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '1px' }}>Calories</span>
          <span style={{ fontSize: '26px', fontWeight: '700' }}>{Math.round(consumed)}</span>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Target: {target} kcal</span>
        </div>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <h2 style={{ fontSize: '22px', fontWeight: '700' }}>Daily Budget</h2>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '200px', fontSize: '14px', lineHeight: '140%' }}>
          You have consumed <strong>{percentage}%</strong> of your daily target energy.
        </p>
        <span style={{ 
          marginTop: '6px',
          alignSelf: 'flex-start',
          padding: '4px 10px', 
          borderRadius: '20px', 
          fontSize: '12px', 
          fontWeight: '600', 
          background: percentage > 100 ? 'rgba(244,63,94,0.15)' : 'rgba(16,185,129,0.15)',
          color: percentage > 100 ? 'var(--color-rose)' : 'var(--color-emerald)'
        }}>
          {percentage > 100 ? `${percentage - 100}% Over Target` : `${100 - percentage}% Remaining`}
        </span>
      </div>
    </div>
  );
}

export function MacroProgressBar({ label, consumed, target, colorClass, unit = 'g' }) {
  const percentage = Math.min(100, Math.round((consumed / (target || 1)) * 100));
  
  return (
    <div className="card metric-card" style={{ padding: '20px' }}>
      <div className="metric-header">
        <span>{label}</span>
        <span style={{ color: 'var(--text-primary)', fontWeight: '600' }}>
          {consumed.toFixed(1)}{unit} <span style={{ color: 'var(--text-muted)', fontSize: '12px', fontWeight: '400' }}>/ {target}{unit}</span>
        </span>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginTop: '4px' }}>
        <span className="metric-value" style={{ fontSize: '22px' }}>{percentage}%</span>
      </div>
      
      <div className="metric-progress-track">
        <div 
          className="metric-progress-bar" 
          style={{ 
            width: `${percentage}%`, 
            background: `var(--color-${colorClass})`,
            boxShadow: `0 0 10px var(--color-${colorClass})`
          }} 
        />
      </div>
    </div>
  );
}
