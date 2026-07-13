import React, { useState } from 'react';

export default function Profile({ profile, onUpdateProfile }) {
  const [weight, setWeight] = useState(profile ? profile.weight : 70);
  const [height, setHeight] = useState(profile ? profile.height : 175);
  const [age, setAge] = useState(profile ? profile.age : 25);
  const [gender, setGender] = useState(profile ? profile.gender : 'Male');
  const [sport, setSport] = useState(profile ? profile.sport : 'General Fitness');
  const [trainingPhase, setTrainingPhase] = useState(profile ? profile.training_phase : 'Rest Day');
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Sync state if profile changes
  React.useEffect(() => {
    if (profile) {
      setWeight(profile.weight);
      setHeight(profile.height);
      setAge(profile.age);
      setGender(profile.gender);
      setSport(profile.sport);
      setTrainingPhase(profile.training_phase);
    }
  }, [profile]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdateProfile({
      weight: parseFloat(weight),
      height: parseFloat(height),
      age: parseInt(age),
      gender,
      sport,
      training_phase: trainingPhase
    });
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const sportsList = ["General Fitness", "Bodybuilder", "Sprinting", "Marathon", "Cricket"];
  const phasesList = ["Rest Day", "Bulk", "Cut", "Competition Day"];

  return (
    <div className="animate-fade-in grid-cols-3" style={{ alignItems: 'flex-start' }}>
      
      {/* Left Column: Form Edit */}
      <div className="grid-span-2 card" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: '700' }}>Athlete Configuration</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
            Update your physical parameters and training phase. The engine will dynamically adjust your target calories and macro budgets.
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          
          <div className="grid-cols-2" style={{ gap: '20px' }}>
            <div className="form-group">
              <label>Weight (kg)</label>
              <input 
                type="number" 
                className="form-input" 
                value={weight} 
                onChange={(e) => setWeight(e.target.value)}
                min="30" 
                max="250"
                step="0.5"
                required
              />
            </div>
            
            <div className="form-group">
              <label>Height (cm)</label>
              <input 
                type="number" 
                className="form-input" 
                value={height} 
                onChange={(e) => setHeight(e.target.value)}
                min="100" 
                max="250"
                step="1"
                required
              />
            </div>
          </div>

          <div className="grid-cols-2" style={{ gap: '20px' }}>
            <div className="form-group">
              <label>Age</label>
              <input 
                type="number" 
                className="form-input" 
                value={age} 
                onChange={(e) => setAge(e.target.value)}
                min="12" 
                max="100"
                required
              />
            </div>
            
            <div className="form-group">
              <label>Gender</label>
              <select className="form-select" value={gender} onChange={(e) => setGender(e.target.value)}>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="grid-cols-2" style={{ gap: '20px' }}>
            <div className="form-group">
              <label>Primary Sport Profile</label>
              <select className="form-select" value={sport} onChange={(e) => setSport(e.target.value)}>
                {sportsList.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label>Active Training Phase</label>
              <select className="form-select" value={trainingPhase} onChange={(e) => setTrainingPhase(e.target.value)}>
                {phasesList.map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginTop: '10px' }}>
            <button type="submit" className="btn btn-primary" style={{ padding: '12px 30px' }}>
              Save & Recalculate Targets
            </button>
            {saveSuccess && (
              <span style={{ color: 'var(--color-emerald)', fontSize: '14px', fontWeight: '600' }}>
                ✓ Profile saved! Targets updated.
              </span>
            )}
          </div>
        </form>
      </div>

      {/* Right Column: Calculated Targets Card */}
      {profile && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <div className="card" style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '20px', 
            border: '1px solid rgba(139, 92, 246, 0.25)', 
            boxShadow: 'var(--shadow-glow)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--color-purple)', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px' }}>
                Calculated Daily Goal
              </span>
              <h3 style={{ fontSize: '24px', fontWeight: '800', marginTop: '6px' }}>Athlete Macros</h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Calories */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
                <span style={{ color: 'var(--text-secondary)', fontWeight: '500' }}>Daily Energy</span>
                <span style={{ fontSize: '20px', fontWeight: '700', color: '#fff' }}>{profile.calorie_target} <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>kcal</span></span>
              </div>

              {/* Protein */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
                <span style={{ color: 'var(--text-secondary)', fontWeight: '500' }}>Protein (1.5 - 2.2x bodyweight)</span>
                <span style={{ fontSize: '20px', fontWeight: '700', color: 'var(--color-purple)' }}>{profile.protein_target} <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>g</span></span>
              </div>

              {/* Carbs */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
                <span style={{ color: 'var(--text-secondary)', fontWeight: '500' }}>Carbohydrates</span>
                <span style={{ fontSize: '20px', fontWeight: '700', color: 'var(--color-cyan)' }}>{profile.carbs_target} <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>g</span></span>
              </div>

              {/* Fats */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '6px' }}>
                <span style={{ color: 'var(--text-secondary)', fontWeight: '500' }}>Fats</span>
                <span style={{ fontSize: '20px', fontWeight: '700', color: 'var(--color-amber)' }}>{profile.fat_target} <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>g</span></span>
              </div>
            </div>
            
            <div style={{ padding: '12px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', fontSize: '12px', color: 'var(--text-muted)', lineHeight: '140%', textAlign: 'center' }}>
              Base BMR targets computed using Harris-Benedict formulas with multiplier adjustments for <strong>{profile.sport}</strong> during <strong>{profile.training_phase}</strong>.
            </div>
          </div>
          
        </div>
      )}

    </div>
  );
}
