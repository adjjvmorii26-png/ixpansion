import React, { createContext, useContext, useState, useEffect } from 'react';

const DashboardContext = createContext();

const useDashboard = () => useContext(DashboardContext);

const DashboardProvider = ({children, token}) => {
  const [vibeState, setVibeState] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch vibe state
        const vibeResponse = await fetch('/api/vibebot/state', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const vibeData = await vibeResponse.json();
        setVibeState(vibeData);
        
        // Fetch enhanced graph data
        const graphResponse = await fetch('/api/emergent_skills/list', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const graphDataResult = await graphResponse.json();
        setGraphData({
          skills: graphDataResult,
          lastUpdated: new Date().toISOString()
        });
      } catch (err) {
        console.error('Dashboard data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [token]);

  return (
    <DashboardContext.Provider value={{vibeState, graphData, loading, useDashboard}}>
      {children}
    </DashboardContext.Provider>
  );
};

export {DashboardProvider, useDashboard};
