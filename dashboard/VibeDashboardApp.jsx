import React from 'react';
import { DashboardProvider, useDashboard } from './DashboardContext';
import VibeDashboardFull from './components/VibeDashboardFull';
import PulseFlow from './components/PulseFlow';

const VibeDashboardApp = () => {
  // Never ship a credential in the client bundle. Configure VIBE_BOT
  // through the build/runtime environment when the API requires auth.
  const token = process.env.VIBE_BOT || '';
  const { graphData, loading } = useDashboard();

  if (loading) return <div>Loading VibeBot Dashboard...</div>;

  const { nodes = [], edges = [] } = graphData || {};

  return (
    <div style={{ minHeight: '100vh', background: '#1a1a24', color: '#e0e0e0' }}>
      <DashboardProvider token={token}>
        <VibeDashboardFull token={token} />
      </DashboardProvider>
      {nodes.length > 0 && (
        <PulseFlow nodes={nodes} edges={edges} width={window.innerWidth} height={window.innerHeight * 0.6} />
      )}
    </div>
  );
};

export default VibeDashboardApp;
