import React from 'react';
import { CalorieRing, MacroProgressBar } from '../components/MetricCard';
import AnalyticsChart from '../components/AnalyticsChart';

export default function Dashboard({ summary, trends, onSelectMeal, onDeleteMeal, apiHost }) {
  if (!summary) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh', color: 'var(--text-secondary)' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="logo-icon" style={{ margin: '0 auto 16px', animation: 'pulse 1.5s infinite' }}>N</div>
          <h3>Syncing dashboard metrics...</h3>
        </div>
      </div>
    );
  }

  const { consumed, target, health_score, meals } = summary;

  // Health Score Rating Text & Color
  let healthRating = "Fair";
  let healthColor = "var(--color-amber)";
  if (health_score >= 80) {
    healthRating = "Excellent";
    healthColor = "var(--color-emerald)";
  } else if (health_score >= 60) {
    healthRating = "Good";
    healthColor = "var(--color-cyan)";
  } else if (health_score > 0 && health_score < 40) {
    healthRating = "Poor";
    healthColor = "var(--color-rose)";
  } else if (health_score === 0) {
    healthRating = "No Meals Logged";
    healthColor = "var(--text-muted)";
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      
      {/* 1. DAILY ENERGY & MACROS ROW */}
      <div className="grid-cols-2">
        <CalorieRing consumed={consumed.calories} target={target.calories} />
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <MacroProgressBar 
            label="Protein (Muscle Synthesis)" 
            consumed={consumed.protein} 
            target={target.protein} 
            colorClass="purple" 
          />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <MacroProgressBar 
              label="Carbohydrates" 
              consumed={consumed.carbs} 
              target={target.carbs} 
              colorClass="cyan" 
            />
            <MacroProgressBar 
              label="Fats" 
              consumed={consumed.fat} 
              target={target.fat} 
              colorClass="amber" 
            />
          </div>
        </div>
      </div>

      {/* 2. WEEKLY CHART & HEALTH SCORE INDEX */}
      <div className="grid-cols-3">
        <div className="grid-span-2">
          <AnalyticsChart data={trends} />
        </div>
        
        {/* Health Score Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', position: 'relative' }}>
          <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
            Dietary Health Index
          </span>
          <div style={{ 
            width: '120px', 
            height: '120px', 
            borderRadius: '50%', 
            border: `6px solid ${health_score > 0 ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.03)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            background: 'radial-gradient(circle, rgba(139,92,246,0.05) 0%, transparent 70%)'
          }}>
            {/* Draw a colored outer ring border */}
            <div style={{
              position: 'absolute',
              top: '-6px',
              left: '-6px',
              right: '-6px',
              bottom: '-6px',
              borderRadius: '50%',
              border: `6px solid ${healthColor}`,
              clipPath: `polygon(50% 50%, -50% -50%, ${health_score >= 25 ? '150% -50%' : '50% -50%'}, ${health_score >= 50 ? '150% 150%' : '50% -50%'}, ${health_score >= 75 ? '-50% 150%' : '50% -50%'}, ${health_score >= 100 ? '-50% -50%' : '50% -50%'})`,
              boxShadow: `0 0 10px ${healthColor}`
            }} />
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span style={{ fontSize: '38px', fontWeight: '800', color: healthColor }}>
                {health_score > 0 ? health_score : '--'}
              </span>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '500' }}>/ 100</span>
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <span style={{ 
              padding: '4px 12px', 
              borderRadius: '20px', 
              fontSize: '13px', 
              fontWeight: '700', 
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid var(--border-color)',
              color: healthColor
            }}>
              {healthRating}
            </span>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '10px', maxWidth: '180px', lineHeight: '140%' }}>
              Score calculated from micronutrients, fibers, protein density, and processing levels.
            </p>
          </div>
        </div>
      </div>

      {/* 3. TODAY'S MEAL LOGS */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700' }}>Today's Logged Meals</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Analyze or edit portions for meals scanned today</p>
        </div>

        {meals.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', border: '2px dashed var(--border-color)', borderRadius: '12px' }}>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>No meals logged yet today.</p>
            <button className="btn btn-primary" onClick={() => onSelectMeal(null)}>
              Scan First Meal
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {meals.map((meal) => {
              const formattedTime = new Date(meal.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
              return (
                <div 
                  key={meal.id} 
                  className="card"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between', 
                    padding: '16px 20px', 
                    background: 'rgba(255,255,255,0.015)',
                    cursor: 'pointer'
                  }}
                  onClick={() => onSelectMeal(meal)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '18px', flexGrow: '1' }}>
                    <div style={{ 
                      width: '60px', 
                      height: '60px', 
                      borderRadius: '10px', 
                      overflow: 'hidden', 
                      border: '1px solid var(--border-color)',
                      flexShrink: 0
                    }}>
                      <img 
                        src={`${apiHost}${meal.image_url}`} 
                        alt="meal log"
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    </div>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '16px', fontWeight: '600', color: '#fff' }}>
                          Meal Scanned
                        </span>
                        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          {formattedTime}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '6px', marginTop: '6px', flexWrap: 'wrap' }}>
                        {meal.food_items && meal.food_items.map((f, i) => (
                          <span 
                            key={i} 
                            style={{ 
                              background: 'rgba(255,255,255,0.04)', 
                              border: '1px solid var(--border-color)',
                              padding: '2px 8px', 
                              borderRadius: '4px', 
                              fontSize: '11px',
                              color: 'var(--text-secondary)'
                            }}
                          >
                            {f.name} ({Math.round(f.weight_g)}g)
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '30px' }}>
                    <div style={{ textAlign: 'right' }}>
                      <span style={{ fontSize: '18px', fontWeight: '700', color: '#fff', display: 'block' }}>
                        {Math.round(meal.total_calories)}
                      </span>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Calories</span>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <span style={{ fontSize: '18px', fontWeight: '700', color: 'var(--color-purple)', display: 'block' }}>
                        {meal.total_protein.toFixed(1)}g
                      </span>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Protein</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <span style={{ 
                        fontSize: '12px', 
                        fontWeight: '700',
                        color: meal.health_score >= 80 ? 'var(--color-emerald)' : meal.health_score >= 60 ? 'var(--color-cyan)' : 'var(--color-amber)',
                        background: meal.health_score >= 80 ? 'rgba(16,185,129,0.08)' : meal.health_score >= 60 ? 'rgba(6,182,212,0.08)' : 'rgba(245,158,11,0.08)',
                        border: `1px solid ${meal.health_score >= 80 ? 'rgba(16,185,129,0.2)' : meal.health_score >= 60 ? 'rgba(6,182,212,0.2)' : 'rgba(245,158,11,0.2)'}`,
                        padding: '2px 8px',
                        borderRadius: '4px'
                      }}>
                        Score: {meal.health_score}
                      </span>
                      
                      <button 
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: 'var(--color-rose)',
                          fontSize: '16px',
                          padding: '6px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          borderRadius: '6px',
                          transition: 'background-color 0.2s',
                          zIndex: 10
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(244,63,94,0.12)'}
                        onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm("Are you sure you want to remove this meal from your daily log?")) {
                            onDeleteMeal(meal.id);
                          }
                        }}
                        title="Remove meal log"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
