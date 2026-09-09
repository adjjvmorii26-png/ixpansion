import React from 'react';

const VibeOverview = ({state}) => {
  if (!state) return <div>Loading vibe state...</div>;

  const vibe = state.current_vibe || 'unknown';
  const intensity = state.intensity || 0;
  const vector = state.vector || {};
  const history = state.history || [];

  // Determine vibe color based on type
  const vibeColors = {
    surge: '#e8a87c',      // warm orange
    ebb: '#41b3a3',       // teal
    ripple: '#96ceb4',    // light green
    tsunami: '#2b5c8f',   // deep blue
    whisper: '#a855f7',   // purple
    crescendo: '#f472b6', // pink
    decay: '#6b7280',     // gray
    explosion: '#f87171', // red
    stillness: '#22c55e', // green
    pulse: '#f6e05e'      // yellow
  };

  const color = vibeColors[vibe] || '#6b7280';

  return (
    <div>
      <h3>🌊 Current System Vibe</h3>
      
      <div style={{background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 16, marginBottom: 16}}>
        <p style={{margin: '8px 0', color: '#cbd5e1'}}>
          <strong>Vibe Type:</strong> {vibe}
        </p>
        <p style={{margin: '8px 0', color: '#cbd5e1'}}>
          <strong>Intensity:</strong> {intensity}
          <div style={{width: '200px', height: '8px', background: '#334155', borderRadius: '4px', overflow: 'hidden', marginTop: '4px'}}>
            <div style={{width: `${intensity * 100}%`, height: '100%', background: color, transition: 'width 0.3s'}}>
            </div>
          </div>
        </p>
      </div>

      <div style={{background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 16, marginBottom: 16}}>
        <p style={{margin: '8px 0', color: '#cbd5e1'}}>
          <strong>Resonance Vectors:</strong>
        </p>
        <div style={{display: 'grid', gap: '12px', marginTop: '8px'}}>
          {['coherence', 'entropy', 'creativity', 'stability', 'consciousness', 'resonance', 'harmony', 'discord', 'growth', 'decay'].map(key => (
            <div key={key} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline'}}>
              <span style={{color: '#9ca3af', fontSize: '0.8em'}}>{key}:</span>
              <span style={{color: color, fontWeight: 'bold'}}>
                {vector[key] !== undefined ? vector[key].toFixed(2) : 'N/A'}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div style={{background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 16}}>
        <p style={{margin: '8px 0', color: '#cbd5e1'}}>
          <strong>Pulse History:</strong> {history.length} pulses recorded
        </p>
        <p style={{margin: '4px 0 0 0', color: '#64748b', fontSize: '0.8em'}}>
          Latest: {history.length > 0 ? history[history.length - 1].type || 'unknown' : 'none'}
        </p>
      </div>
    </div>
  );
};

export default VibeOverview;
