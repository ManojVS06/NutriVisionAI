import React, { useState } from 'react';

export default function Settings({ apiHost, setApiHost }) {
  const [hostInput, setHostInput] = useState(apiHost || 'http://127.0.0.1:8000');
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    localStorage.setItem('api_host_url', hostInput.trim());
    setApiHost(hostInput.trim());
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  return (
    <div className="animate-fade-in card" style={{ maxWidth: '600px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h2 style={{ fontSize: '22px', fontWeight: '700' }}>System Configuration</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
          Manage local developer settings, API endpoints, and LLM credentials.
        </p>
      </div>

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        
        <div className="form-group">
          <label>Backend API Host URL</label>
          <input 
            type="text" 
            className="form-input" 
            placeholder="http://127.0.0.1:8000"
            value={hostInput}
            onChange={(e) => setHostInput(e.target.value)}
            required
          />
          <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '4px' }}>
            The endpoint where the FastAPI backend is running. Default is <code>http://127.0.0.1:8000</code>.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginTop: '10px' }}>
          <button type="submit" className="btn btn-primary" style={{ padding: '12px 30px' }}>
            Save Configurations
          </button>
          {saveSuccess && (
            <span style={{ color: 'var(--color-emerald)', fontSize: '14px', fontWeight: '600' }}>
              ✓ Settings saved locally!
            </span>
          )}
        </div>
      </form>

      <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '20px', marginTop: '10px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '8px' }}>Project Database Seed Status</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: '145%' }}>
          Your local SQLite database is populated with reference IFCT nutrient categories and a 7-day mock eating history for the <code>demouser</code>. To reset the database at any time, run:
        </p>
        <code style={{ 
          display: 'block', 
          padding: '10px 14px', 
          borderRadius: '8px', 
          background: 'rgba(255,255,255,0.03)', 
          border: '1px solid var(--border-color)', 
          fontSize: '12px',
          color: 'var(--color-purple)',
          marginTop: '10px',
          fontFamily: 'monospace'
        }}>
          python backend/database/seed.py
        </code>
      </div>
    </div>
  );
}
