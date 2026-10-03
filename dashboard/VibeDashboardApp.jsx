import React from 'react';
import { DashboardProvider, useDashboard } from './DashboardContext';
import VibeDashboardFull from './components/VibeDashboardFull';
import PulseFlow from './components/PulseFlow';

const DashboardContent = () => {
  const { graphData, loading } = useDashboard();

  if (loading) return <div>Loading VibeBot Dashboard...</div>;

  const { nodes = [], edges = [] } = graphData || {};

  return (
    <>
      <VibeDashboardFull token="" />
      {nodes.length > 0 && (
        <PulseFlow
          nodes={nodes}
          edges={edges}
          width={window.innerWidth}
          height={window.innerHeight * 0.6}
        />
      )}
    </>
  );
};

const VibeDashboardApp = () => {
  // Never ship a credential in the client bundle.
  // Dashboard reads are handled by the server-side route contract.
  return (
    <div style={{ minHeight: '100vh', background: '#1a1a24', color: '#e0e0e0' }}>
      <DashboardProvider>
        <DashboardContent />
      </DashboardProvider>
    </div>
  );
};

export default VibeDashboardApp;
