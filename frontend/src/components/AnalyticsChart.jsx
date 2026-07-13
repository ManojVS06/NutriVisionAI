import React, { useState } from 'react';

export default function AnalyticsChart({ data }) {
  const [metric, setMetric] = useState('calories'); // 'calories' or 'protein'
  
  if (!data || data.length === 0) {
    return <div style={{ color: 'var(--text-muted)' }}>No trend data available</div>;
  }

  // Find max value to scale the Y axis
  const getValue = (d) => d[metric] || 0;
  const getTarget = (d) => metric === 'calories' ? d.target_calories : d.target_protein;
  
  const values = data.map(getValue);
  const targets = data.map(getTarget);
  const allValues = [...values, ...targets];
  const maxVal = Math.max(...allValues, 100) * 1.15; // 15% padding at top

  // SVG dimensions
  const width = 500;
  const height = 220;
  const paddingLeft = 40;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 30;

  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  // Calculate coordinates for points
  const points = data.map((d, index) => {
    const x = paddingLeft + (index / (data.length - 1)) * chartWidth;
    const y = paddingTop + chartHeight - (getValue(d) / maxVal) * chartHeight;
    return { x, y, label: d.date, val: getValue(d) };
  });

  // Calculate coordinates for target line
  const targetPoints = data.map((d, index) => {
    const x = paddingLeft + (index / (data.length - 1)) * chartWidth;
    const y = paddingTop + chartHeight - (getTarget(d) / maxVal) * chartHeight;
    return { x, y, val: getTarget(d) };
  });

  // Build the SVG path strings
  const linePath = points.length > 0 
    ? `M ${points[0].x} ${points[0].y} ` + points.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')
    : '';

  const targetPath = targetPoints.length > 0
    ? `M ${targetPoints[0].x} ${targetPoints[0].y} ` + targetPoints.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')
    : '';

  // Area path for filling under the line
  const areaPath = points.length > 0
    ? `${linePath} L ${points[points.length - 1].x} ${paddingTop + chartHeight} L ${points[0].x} ${paddingTop + chartHeight} Z`
    : '';

  // Generate grid values for Y axis (4 increments)
  const yTicks = [0, 0.33, 0.66, 1].map(pct => {
    const val = pct * maxVal;
    const y = paddingTop + chartHeight - (val / maxVal) * chartHeight;
    return { y, label: Math.round(val) };
  });

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700' }}>Weekly Analytics</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Logged history vs Daily targets</p>
        </div>
        <div style={{ display: 'inline-flex', background: 'rgba(255,255,255,0.04)', padding: '4px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <button 
            className="btn"
            style={{ 
              padding: '6px 12px', 
              fontSize: '13px', 
              borderRadius: '6px',
              background: metric === 'calories' ? 'var(--grad-primary)' : 'transparent',
              color: '#fff',
              boxShadow: metric === 'calories' ? 'var(--shadow-sm)' : 'none'
            }}
            onClick={() => setMetric('calories')}
          >
            Calories
          </button>
          <button 
            className="btn"
            style={{ 
              padding: '6px 12px', 
              fontSize: '13px', 
              borderRadius: '6px',
              background: metric === 'protein' ? 'var(--grad-primary)' : 'transparent',
              color: '#fff',
              boxShadow: metric === 'protein' ? 'var(--shadow-sm)' : 'none'
            }}
            onClick={() => setMetric('protein')}
          >
            Protein
          </button>
        </div>
      </div>

      <div style={{ position: 'relative', width: '100%' }}>
        <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="auto" style={{ overflow: 'visible' }}>
          {/* Horizontal Grid Lines & Y Labels */}
          {yTicks.map((tick, i) => (
            <g key={i}>
              <line 
                x1={paddingLeft} 
                y1={tick.y} 
                x2={width - paddingRight} 
                y2={tick.y} 
                stroke="rgba(255,255,255,0.05)" 
                strokeWidth="1"
              />
              <text 
                x={paddingLeft - 8} 
                y={tick.y + 4} 
                fill="var(--text-muted)" 
                fontSize="10" 
                textAnchor="end"
                fontFamily="Outfit"
              >
                {tick.label}
              </text>
            </g>
          ))}

          {/* Area Fill */}
          {points.length > 0 && (
            <path 
              d={areaPath} 
              fill={metric === 'calories' ? 'rgba(139, 92, 246, 0.08)' : 'rgba(6, 182, 212, 0.08)'}
            />
          )}

          {/* Target Baseline */}
          {targetPoints.length > 0 && (
            <path 
              d={targetPath} 
              fill="none" 
              stroke="var(--color-rose)" 
              strokeWidth="2" 
              strokeDasharray="4 4"
              opacity="0.65"
            />
          )}

          {/* Active / Consumed line */}
          {points.length > 0 && (
            <path 
              d={linePath} 
              fill="none" 
              stroke={metric === 'calories' ? 'var(--color-purple)' : 'var(--color-cyan)'} 
              strokeWidth="3.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* Data Points */}
          {points.map((p, i) => (
            <g key={i}>
              <circle 
                cx={p.x} 
                cy={p.y} 
                r="4.5" 
                fill="#fff" 
                stroke={metric === 'calories' ? 'var(--color-purple)' : 'var(--color-cyan)'} 
                strokeWidth="2.5"
              />
              {/* X Labels */}
              <text 
                x={p.x} 
                y={height - 8} 
                fill="var(--text-secondary)" 
                fontSize="11" 
                textAnchor="middle"
                fontFamily="Outfit"
                fontWeight="500"
              >
                {p.label}
              </text>
            </g>
          ))}
        </svg>
      </div>

      <div style={{ display: 'flex', gap: '20px', fontSize: '13px', color: 'var(--text-secondary)', justifyContent: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '12px', height: '4px', background: metric === 'calories' ? 'var(--color-purple)' : 'var(--color-cyan)', borderRadius: '2px' }} />
          <span>Consumed today</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '12px', height: '0px', borderTop: '2px dashed var(--color-rose)', borderRadius: '2px' }} />
          <span>Daily Target ({metric === 'calories' ? 'kcal' : 'g'})</span>
        </div>
      </div>
    </div>
  );
}
