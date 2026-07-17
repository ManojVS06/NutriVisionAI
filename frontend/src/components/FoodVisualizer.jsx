import React, { useState } from 'react';

export default function FoodVisualizer({ meal, onSavePortions, apiHost = 'http://127.0.0.1:8000' }) {
  const [activeStep, setActiveStep] = useState('detection'); // 'original', 'detection', 'segmentation', 'depth'
  const [weights, setWeights] = useState({});
  const [isEditing, setIsEditing] = useState(false);

  if (!meal) return null;

  // Initialize weights if not set
  if (isEditing && Object.keys(weights).length === 0 && meal.food_items) {
    const initialWeights = {};
    meal.food_items.forEach(item => {
      initialWeights[item.id] = item.weight_g;
    });
    setWeights(initialWeights);
  }

  const steps = [
    {
      id: 'original',
      label: '1. Input Image',
      image: meal.image_url,
      description: 'The raw food plate image uploaded by the user, normalized and contrast-adjusted.',
      badgeColor: 'var(--text-secondary)'
    },
    {
      id: 'detection',
      label: '2. Grounding DINO',
      image: meal.processed_url,
      description: 'Grounding DINO performs zero-shot open-vocabulary object localization to output precise bounding boxes, which are then refined by CLIP classification.',
      badgeColor: 'var(--color-purple)'
    },
    {
      id: 'segmentation',
      label: '3. SAM2 Masks',
      image: meal.mask_url,
      description: 'Segment Anything Model (SAM2) generates exact contours/masks of the food to compute real-world surface area.',
      badgeColor: 'var(--color-cyan)'
    },
    {
      id: 'depth',
      label: '4. Depth Anything V2',
      image: meal.depth_url,
      description: 'Monocular depth model estimates the Z-axis height profile of the plate structure to calculate food volume.',
      badgeColor: 'var(--color-rose)'
    }
  ];

  const currentStep = steps.find(s => s.id === activeStep) || steps[1];

  const handleSliderChange = (id, val) => {
    setWeights(prev => ({
      ...prev,
      [id]: parseFloat(val)
    }));
  };

  const handleSave = () => {
    const payload = Object.keys(weights).map(id => ({
      id: parseInt(id),
      weight_g: weights[id]
    }));
    onSavePortions(meal.id, payload);
    setIsEditing(false);
    setWeights({});
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      
      {/* 1. PIPELINE VISUALIZATION TAB GRID */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: '700' }}>AI Model Pipeline Viewer</h2>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: '4px', flexWrap: 'wrap' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Pipeline:</span>
              <span style={{
                padding: '2px 8px',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '700',
                textTransform: 'uppercase',
                background: 
                  meal.detection_method === 'gdino_clip' ? 'rgba(16, 185, 129, 0.1)' :
                  meal.detection_method === 'gemini_vision' ? 'rgba(139, 92, 246, 0.1)' :
                  meal.detection_method === 'demo' ? 'rgba(6, 182, 212, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                color:
                  meal.detection_method === 'gdino_clip' ? 'var(--color-emerald)' :
                  meal.detection_method === 'gemini_vision' ? 'var(--color-purple)' :
                  meal.detection_method === 'demo' ? 'var(--color-cyan)' : 'var(--color-rose)',
                border: '1px solid currentColor'
              }}>
                {
                  meal.detection_method === 'gdino_clip' ? 'Grounding DINO + CLIP (Local)' :
                  meal.detection_method === 'gemini_vision' ? 'Gemini 2.0 Flash' :
                  meal.detection_method === 'demo' ? 'Demo Simulation' : 'OpenCV Fallback'
                }
              </span>
              {meal.quality_score !== undefined && (
                <>
                  <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>•</span>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                    Image Quality: <strong style={{ color: meal.quality_score >= 75 ? 'var(--color-emerald)' : 'var(--color-rose)' }}>{Math.round(meal.quality_score)}/100</strong>
                  </span>
                </>
              )}
            </div>
          </div>
          <div style={{ display: 'inline-flex', background: 'rgba(255,255,255,0.03)', padding: '4px', borderRadius: '8px', border: '1px solid var(--border-color)', flexWrap: 'wrap' }}>
            {steps.map(s => (
              <button
                key={s.id}
                className="btn"
                style={{
                  padding: '6px 12px',
                  fontSize: '13px',
                  borderRadius: '6px',
                  background: activeStep === s.id ? 'var(--grad-primary)' : 'transparent',
                  color: '#fff',
                  boxShadow: activeStep === s.id ? 'var(--shadow-sm)' : 'none'
                }}
                onClick={() => setActiveStep(s.id)}
              >
                {s.label.split('. ')[1]}
              </button>
            ))}
          </div>
        </div>

        {/* Visualizer Display Box */}
        <div className="grid-cols-2" style={{ alignItems: 'center' }}>
          <div style={{ 
            borderRadius: '12px', 
            overflow: 'hidden', 
            border: '1px solid var(--border-color)',
            background: '#05070c',
            aspectRatio: '1',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative'
          }}>
            {currentStep.image ? (
              <img 
                src={`${apiHost}${currentStep.image}`} 
                alt={currentStep.label}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            ) : (
              <span style={{ color: 'var(--text-muted)' }}>Image failed to load</span>
            )}
            
            <span style={{
              position: 'absolute',
              top: '12px',
              left: '12px',
              padding: '4px 10px',
              borderRadius: '20px',
              fontSize: '11px',
              fontWeight: '700',
              textTransform: 'uppercase',
              color: '#fff',
              background: currentStep.badgeColor,
              boxShadow: '0 2px 8px rgba(0,0,0,0.5)'
            }}>
              {currentStep.label}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: currentStep.badgeColor }} />
              <h3 style={{ fontSize: '18px', fontWeight: '600' }}>Pipeline Step Info</h3>
            </div>
            
            <p style={{ color: 'var(--text-secondary)', fontSize: '15px', lineHeight: '150%' }}>
              {currentStep.description}
            </p>

            <div style={{ 
              marginTop: '10px', 
              padding: '16px', 
              borderRadius: '12px', 
              background: 'rgba(255,255,255,0.02)', 
              border: '1px solid var(--border-color)',
              fontSize: '13px'
            }}>
              <span style={{ fontWeight: '600', color: 'var(--color-cyan)', display: 'block', marginBottom: '6px' }}>PORTION MATHEMATICS:</span>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px', color: 'var(--text-secondary)' }}>
                <li>• Reference object plate diameter assumes <strong>26.0 cm</strong></li>
                <li>• Estimated Volume (cm³) = Area (cm²) × Height (cm) from depth map</li>
                <li>• Estimated Weight (grams) = Volume (cm³) × Food Density (g/cm³)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 2. MEAL INGREDIENTS TABLE & ADJUSTMENTS */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: '700' }}>Detected Portion Weights</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Verify and manually override weights if needed</p>
          </div>
          {!isEditing ? (
            <button 
              className="btn btn-secondary" 
              style={{ padding: '8px 16px', fontSize: '13px' }}
              onClick={() => setIsEditing(true)}
            >
              Adjust Portions
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '8px 16px', fontSize: '13px' }}
                onClick={() => { setIsEditing(false); setWeights({}); }}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                style={{ padding: '8px 16px', fontSize: '13px' }}
                onClick={handleSave}
              >
                Save Changes
              </button>
            </div>
          )}
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', minWidth: '600px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '13px' }}>
                <th style={{ padding: '12px 8px' }}>Food Name</th>
                <th style={{ padding: '12px 8px' }}>Estimated Volume</th>
                <th style={{ padding: '12px 8px' }}>Portion Weight</th>
                <th style={{ padding: '12px 8px' }}>Model Confidence</th>
                <th style={{ padding: '12px 8px' }}>Calories</th>
                <th style={{ padding: '12px 8px' }}>Protein</th>
                <th style={{ padding: '12px 8px' }}>Carbs</th>
                <th style={{ padding: '12px 8px' }}>Fat</th>
              </tr>
            </thead>
            <tbody>
              {meal.food_items && meal.food_items.map((item) => (
                <tr key={item.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', fontSize: '14px' }}>
                  <td style={{ padding: '16px 8px', fontWeight: '500', color: '#fff' }}>{item.name}</td>
                  <td style={{ padding: '16px 8px', color: 'var(--text-secondary)' }}>{item.volume_cm3} cm³</td>
                  <td style={{ padding: '16px 8px', width: '220px' }}>
                    {isEditing ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                          <span style={{ color: 'var(--color-cyan)', fontWeight: '600' }}>
                            {weights[item.id] !== undefined ? weights[item.id] : item.weight_g}g
                          </span>
                        </div>
                        <input 
                          type="range" 
                          min="20" 
                          max="500" 
                          step="5"
                          value={weights[item.id] !== undefined ? weights[item.id] : item.weight_g}
                          onChange={(e) => handleSliderChange(item.id, e.target.value)}
                          style={{ 
                            width: '100%', 
                            accentColor: 'var(--color-purple)', 
                            background: 'rgba(255,255,255,0.1)', 
                            height: '4px', 
                            borderRadius: '2px', 
                            cursor: 'pointer' 
                          }}
                        />
                      </div>
                    ) : (
                      <span style={{ fontWeight: '600', color: 'var(--color-cyan)' }}>{item.weight_g} g</span>
                    )}
                  </td>
                  <td style={{ padding: '16px 8px' }}>
                    <span style={{
                      fontWeight: '700',
                      color:
                        item.confidence >= 0.70 ? 'var(--color-emerald)' :
                        item.confidence >= 0.50 ? 'var(--color-amber)' : 'var(--color-rose)'
                    }}>
                      {item.confidence !== undefined ? `${Math.round(item.confidence * 100)}%` : '100%'}
                    </span>
                  </td>
                  <td style={{ padding: '16px 8px', color: '#fff' }}>{Math.round(item.calories)} kcal</td>
                  <td style={{ padding: '16px 8px', color: 'var(--color-emerald)', fontWeight: '500' }}>{item.protein}g</td>
                  <td style={{ padding: '16px 8px', color: 'var(--text-secondary)' }}>{item.carbs}g</td>
                  <td style={{ padding: '16px 8px', color: 'var(--text-secondary)' }}>{item.fat}g</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
    </div>
  );
}
