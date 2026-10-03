import React, { createContext, useContext, useState, useEffect } from 'react';

const DashboardContext = createContext();

const useDashboard = () => useContext(DashboardContext);

const DashboardProvider = ({children}) => {
  const [vibeState, setVibeState] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const vibeResponse = await fetch('/api/vibebot/state');
        const vibeData = await vibeResponse.json();
        setVibeState(vibeData);

        const graphResponse = await fetch('/api/emergent_skills/list');
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
  }, []);

  return (
    <DashboardContext.Provider value={{vibeState, graphData, loading, useDashboard}}>
      {children}
    </DashboardContext.Provider>
  );
};

export {DashboardProvider, useDashboard};
