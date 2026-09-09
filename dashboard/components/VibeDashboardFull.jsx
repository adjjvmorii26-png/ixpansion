import React, { useEffect, useState } from 'react';
import VibeOverview from './VibeOverview';
import ResonanceGraph from './ResonanceGraph';

const VibeDashboardFull = ({token}) => {
  const [vibeState, setVibeState] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/vibebot/state', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setVibeState(data);
      } catch (err) {
        console.error('Failed to fetch data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [token]);

  if (loading) return <div>Loading vibe dashboard...</div>;
  if (!vibeState) return <div>No data available</div>;

  return (
    <div style={{fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', background: '#1a1a24', color: '#e0e0e0', minHeight: '800px'}}>
      <header style={{borderBottom: '2px solid #333344', paddingBottom: '15px', marginBottom: '20px'}}>
        <h1 style={{margin: 0, color: '#e8a87c'}}>🌊 VibeBot Operational Dashboard</h1>
        <p style={{margin: '8px 0 0 0', color: '#888'}}>System Vibe & Resonance State</p>
      </header>
      
      <div style={{display: 'grid', gap: '20px', gridTemplateAreas: '"overview graph"'}}>
        <div style={{gridArea: 'overview', background: '#242433', borderRadius: 8, padding: '20px'}}>
          <VibeOverview state={vibeState} />
        </div>
        <div style={{gridArea: 'graph', background: '#242433', borderRadius: 8, padding: '20px'}}>
          <ResonanceGraph token={token} vibeState={vibeState} />
        </div>
      </div>
      
      <footer style={{marginTop: '20px', paddingTop: '15px', borderTop: '1px solid #333', color: '#888', fontSize: '0.8em'}}>
        <p>Last updated: {new Date().toLocaleTimeString()} | VibeBot Orchestrator v2.0</p>
      </footer>
    </div>
  );
};

export default VibeDashboardFull;
