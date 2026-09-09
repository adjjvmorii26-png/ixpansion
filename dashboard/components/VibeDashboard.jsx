import React, { useEffect, useState } from 'react';

const VibeDashboard = ({token}) => {
  const [vibe, setVibe] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    
    const fetchVibe = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/vibebot/state', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setVibe(data);
      } catch (err) {
        console.error('Failed to fetch vibe state:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchVibe();
    const interval = setInterval(fetchVibe, 30000);
    return () => clearInterval(interval);
  }, [token]);

  if (loading) return <div>Loading vibe state...</div>;

  if (!vibe) return <div>No vibe data available</div>;

  return (
    <div style={{border: '1px solid #333', borderRadius: 8, padding: 16, background: '#1a1a24'}}>
      <h3>🌊 System Vibe</h3>
      <p><strong>Current Type:</strong> {vibe.current_vibe}</p>
      <p><strong>Intensity:</strong> {vibe.intensity}</p>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px', gap: 12}}>
        {Object.entries(vibe.vector).map(([key, value]) => (
          <div key={key} style={{border: '1px solid #444', borderRadius: 4, padding: 8, background: '#242433'}}>
            <strong>{key}:</strong> {value}
          </div>
        ))}
      </div>
      <p><strong>History count:</strong> {vibe.history?.length || 0}</p>
    </div>
  );
};

export default VibeDashboard;
