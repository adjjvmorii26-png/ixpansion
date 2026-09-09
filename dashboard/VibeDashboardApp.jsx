import React, { useEffect } from 'react';
import { DashboardProvider, useDashboard } from './DashboardContext';
import VibeDashboardFull from './components/VibeDashboardFull';
import { ResonanceGraph } from './components/ResonanceGraph';
import PulseFlow from './components/PulseFlow';
import VibeOverview from './components/VibeOverview';

const VibeDashboardApp = () => {
  // Get token from environment or use default
  const token = process.env.VIBE_BOT || '9bb7866ec849391842c1f93732109d4883c7e98849060447b98436a202f41a40';
  
  const {vibeState, graphData, loading, useDashboard} = useDashboard();
  
  useEffect(() => {
    // Initialize with token
    if (token) {
      // DashboardProvider already fetches data on mount
    }
  }, [token]);

  if (loading) return <div>Loading VibeBot Dashboard...</div>;

  const {nodes = [], edges = []} = graphData || {};

  return (
    <div style={{minHeight: '100vh', background: '#1a1a24', color: '#e0e0e0'}}>
      <DashboardProvider token={token}>
        <VibeDashboardFull token={token} />
      </DashboardProvider>
      
      {/* Pulse Flow Layer - overlay */}
      {nodes && nodes.length > 0 && (
        <PulseFlow
          nodes={nodes}
          edges={edges || []}
          width={window.innerWidth}
          height={window.innerHeight * 0.6}
        />
      )}
    </div>
  );
};

export default VibeDashboardApp;
