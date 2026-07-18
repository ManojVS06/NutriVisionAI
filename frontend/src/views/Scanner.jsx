import React, { useState } from 'react';
import FoodVisualizer from '../components/FoodVisualizer';

export default function Scanner({ 
  activeMeal, 
  setActiveMeal, 
  onUploadFile, 
  onSelectDemo, 
  onSavePortions, 
  isLoading, 
  apiHost,
  error,
  setError
}) {
  const [dragActive, setDragActive] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);

  // Simulated multi-step loading tracker
  React.useEffect(() => {
    let interval;
    if (isLoading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep(prev => {
          if (prev >= 5) {
            clearInterval(interval);
            return 5;
          }
          return prev + 1;
        });
      }, 1500); // 1.5s per step
    } else {
      setLoadingStep(0);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUploadFile(e.target.files[0]);
    }
  };

  const loadingMessages = [
    "Assessing image quality gates (blur, exposure, plate presence)...",
    "Running Grounding DINO open-vocabulary detector...",
    "Refining class scores against 155 IFCT foods with CLIP...",
    "Segmenting exact contours with SAM2 Hiera...",
    "Estimating 3D portion volume with Depth Anything V2...",
    "Running biochemical sanity validator & generating coach advice..."
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      
      {/* View Title */}
      {!activeMeal && !isLoading && (
        <div style={{ textAlign: 'center', margin: '40px auto 20px', maxWidth: '600px' }}>
          <h1 style={{ fontSize: '36px', fontWeight: '800', marginBottom: '12px', background: 'linear-gradient(135deg, #fff 30%, var(--text-secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            AI Meal Scanner
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '16px', lineHeight: '150%' }}>
            Upload a photo of your plate or select one of our pre-defined Indian meal templates to run the computer vision portion and nutrient analysis engine.
          </p>
        </div>
      )}

      {/* Quality Gate Rejection Error Banner */}
      {error && !isLoading && !activeMeal && (
        <div className="card" style={{
          borderLeft: '4px solid var(--color-rose)',
          background: 'linear-gradient(to right, rgba(239,68,68,0.03), rgba(17,24,39,0.7))',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          padding: '20px',
          position: 'relative'
        }}>
          <button 
            style={{ position: 'absolute', top: '12px', right: '12px', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '16px' }}
            onClick={() => setError(null)}
          >
            ✕
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '20px' }}>⚠️</span>
            <h4 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--color-rose)' }}>Image Quality Rejection Gate</h4>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px', lineHeight: '145%' }}>
            {error}
          </p>
        </div>
      )}

      {/* 1. LOADING OVERLAY STATE */}
      {isLoading && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 40px', gap: '30px', background: 'rgba(17,24,39,0.9)' }}>
          {/* Glowing Spinner */}
          <div style={{ position: 'relative', width: '80px', height: '80px' }}>
            <div style={{
              width: '100%',
              height: '100%',
              borderRadius: '50%',
              border: '4px solid rgba(139, 92, 246, 0.1)',
              borderTopColor: 'var(--color-purple)',
              animation: 'spin 1s linear infinite'
            }} />
            <div style={{
              position: 'absolute',
              top: '4px',
              left: '4px',
              right: '4px',
              bottom: '4px',
              borderRadius: '50%',
              border: '4px solid rgba(6, 182, 212, 0.1)',
              borderBottomColor: 'var(--color-cyan)',
              animation: 'spin 1.5s linear infinite reverse'
            }} />
          </div>

          <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <h3 style={{ fontSize: '20px', fontWeight: '700' }}>Processing Plate Image</h3>
            <p style={{ color: 'var(--color-cyan)', fontSize: '15px', fontWeight: '600', animation: 'pulse 1s infinite' }}>
              {loadingMessages[loadingStep]}
            </p>
            
            {/* Step Indicators */}
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginTop: '12px' }}>
              {loadingMessages.map((_, idx) => (
                <span 
                  key={idx} 
                  style={{ 
                    width: '30px', 
                    height: '6px', 
                    borderRadius: '3px',
                    background: idx <= loadingStep ? 'var(--color-purple)' : 'rgba(255,255,255,0.05)',
                    boxShadow: idx === loadingStep ? 'var(--shadow-glow)' : 'none'
                  }} 
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 2. UPLOAD & CHOOSE DEMO SCREEN */}
      {!activeMeal && !isLoading && (
        <div className="grid-cols-3" style={{ alignItems: 'stretch' }}>
          
          {/* Upload Card */}
          <div className="grid-span-2 card" style={{ padding: '0px', overflow: 'hidden' }}>
            <div 
              style={{
                width: '100%',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '40px',
                border: dragActive ? '2px dashed var(--color-purple)' : '2px dashed var(--border-color)',
                borderRadius: 'var(--radius-md)',
                background: dragActive ? 'rgba(139, 92, 246, 0.05)' : 'transparent',
                cursor: 'pointer',
                margin: '-1px'
              }}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-upload-input').click()}
            >
              <input 
                id="file-upload-input"
                type="file" 
                style={{ display: 'none' }}
                onChange={handleFileInput}
                accept="image/png, image/jpeg, image/jpg"
              />
              
              {/* Upload Icon */}
              <div className="logo-icon" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', fontSize: '24px', width: '60px', height: '60px', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-purple)', marginBottom: '16px' }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              
              <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>
                Drag & Drop meal image here
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', textAlign: 'center' }}>
                Supports JPEG, PNG. Standard smartphone camera aspect ratios.
              </p>
              
              <button className="btn btn-secondary" style={{ marginTop: '20px', padding: '10px 20px', fontSize: '14px' }}>
                Browse Files
              </button>
            </div>
          </div>

          {/* Demo Meals Selection Card */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '700' }}>Demo Portfolio Templates</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
                Instant simulation with pre-loaded high-fidelity dataset images.
              </p>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <button 
                className="btn btn-secondary" 
                style={{ width: '100%', justifyContent: 'flex-start', padding: '12px 16px' }}
                onClick={() => onSelectDemo('dosa')}
              >
                <span style={{ fontSize: '18px', marginRight: '6px' }}>🥞</span>
                <div style={{ textAlign: 'left' }}>
                  <span style={{ display: 'block', fontWeight: '600', fontSize: '14px' }}>Masala Dosa & Sambar</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Cereal, Pulses (Breakfast combo)</span>
                </div>
              </button>

              <button 
                className="btn btn-secondary" 
                style={{ width: '100%', justifyContent: 'flex-start', padding: '12px 16px' }}
                onClick={() => onSelectDemo('biryani')}
              >
                <span style={{ fontSize: '18px', marginRight: '6px' }}>🍛</span>
                <div style={{ textAlign: 'left' }}>
                  <span style={{ display: 'block', fontWeight: '600', fontSize: '14px' }}>Chicken Biryani & Egg</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Meat, Poultry (High protein lunch)</span>
                </div>
              </button>

              <button 
                className="btn btn-secondary" 
                style={{ width: '100%', justifyContent: 'flex-start', padding: '12px 16px' }}
                onClick={() => onSelectDemo('thali')}
              >
                <span style={{ fontSize: '18px', marginRight: '6px' }}>🍱</span>
                <div style={{ textAlign: 'left' }}>
                  <span style={{ display: 'block', fontWeight: '600', fontSize: '14px' }}>Traditional North-Indian Thali</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Dal, Paneer, Rice, Roti, Salad</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. ACTIVE MEAL DISPLAY SCREEN */}
      {activeMeal && !isLoading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          
          {/* Header Action Row */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button className="btn btn-secondary" onClick={() => setActiveMeal(null)}>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '4px' }}>
                <polyline points="15 18 9 12 15 6" />
              </svg>
              Scan Another Meal
            </button>
            
            <div style={{ display: 'flex', gap: '14px' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '6px 16px', display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block' }}>Meal Health Score</span>
                  <span style={{ fontSize: '16px', fontWeight: '700', color: activeMeal.health_score >= 80 ? 'var(--color-emerald)' : 'var(--color-cyan)' }}>
                    {activeMeal.health_score}/100
                  </span>
                </div>
                <div style={{ width: '1px', height: '24px', background: 'var(--border-color)' }} />
                <div>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block' }}>Total Energy</span>
                  <span style={{ fontSize: '16px', fontWeight: '700', color: '#fff' }}>
                    {Math.round(activeMeal.total_calories)} kcal
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid-cols-3" style={{ alignItems: 'flex-start' }}>
            {/* Left/Middle: Step Visualizer & Portions */}
            <div className="grid-span-2" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
              <FoodVisualizer 
                meal={activeMeal} 
                onSavePortions={onSavePortions} 
                apiHost={apiHost} 
              />
            </div>

            {/* Right: AI Coach Recommendation Panel */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', position: 'sticky', top: '20px' }}>
              
              {/* Aggregated Macro Summary Card */}
              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Meal Nutrient Breakdown</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  
                  {/* Protein */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Protein</span>
                      <span style={{ fontWeight: '600', color: 'var(--color-purple)' }}>{activeMeal.total_protein} g</span>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${Math.min(100, (activeMeal.total_protein / 40) * 100)}%`, background: 'var(--color-purple)' }} />
                    </div>
                  </div>

                  {/* Carbs */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Carbohydrates</span>
                      <span style={{ fontWeight: '600', color: 'var(--color-cyan)' }}>{activeMeal.total_carbs} g</span>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${Math.min(100, (activeMeal.total_carbs / 100) * 100)}%`, background: 'var(--color-cyan)' }} />
                    </div>
                  </div>

                  {/* Fats */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Fats</span>
                      <span style={{ fontWeight: '600', color: 'var(--color-amber)' }}>{activeMeal.total_fat} g</span>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${Math.min(100, (activeMeal.total_fat / 35) * 100)}%`, background: 'var(--color-amber)' }} />
                    </div>
                  </div>

                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-color)', fontSize: '12px', color: 'var(--text-muted)' }}>
                  <div>Fiber: <strong style={{ color: 'var(--text-primary)' }}>{activeMeal.total_fiber}g</strong></div>
                  <div>Sodium: <strong style={{ color: 'var(--text-primary)' }}>{Math.round(activeMeal.total_sodium)}mg</strong></div>
                  <div>Sugar: <strong style={{ color: 'var(--text-primary)' }}>{activeMeal.total_sugar}g</strong></div>
                </div>
              </div>

              {/* Coach Advice Card */}
              <div className="card" style={{ 
                borderLeft: '4px solid var(--color-purple)', 
                background: 'linear-gradient(to right, rgba(139,92,246,0.03), rgba(17,24,39,0.7))',
                display: 'flex',
                flexDirection: 'column',
                gap: '14px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'var(--grad-primary)', display: 'flex', alignItems: 'center', justifyItems: 'center', justifyContent: 'center', fontSize: '15px' }}>🤖</div>
                  <div>
                    <h3 style={{ fontSize: '15px', fontWeight: '700' }}>AI Coach Evaluation</h3>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Athlete Recommendation</span>
                  </div>
                </div>
                
                <div style={{ fontSize: '14px', lineHeight: '155%', color: 'var(--text-secondary)', whiteSpace: 'pre-line' }}>
                  {activeMeal.coach_notes}
                </div>
              </div>

            </div>
          </div>
        </div>
      )}

    </div>
  );
}
