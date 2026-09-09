import React, { useEffect, useState } from 'react';

const ResonanceGraph = ({token, vibeState}) => {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    
    const fetchGraph = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/vibebot/state', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setGraphData(data);
      } catch (err) {
        console.error('Failed to fetch resonance graph data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
    const interval = setInterval(fetchGraph, 15000);
    return () => clearInterval(interval);
  }, [token, vibeState]);

  if (loading) return <div>Loading resonance graph...</div>;
  if (!graphData) return <div>No graph data available</div>;

  const nodes = graphData.visualization?.nodes || [];
  const edges = graphData.visualization?.edges || [];

  return (
    <div style={{border: '1px solid #333', borderRadius: 8, padding: 16, background: '#1a1a24', height: '400px'}}>
      <h3>🔗 Resonance Graph — Module Interconnections</h3>
      <p>Average Resonance: {graphData.visual?.average_resonance || 0}</p>
      
      <div style={{position: 'relative', height: '350px', width: '100%'}}>
        {nodes && edges && nodes.length > 0 && (
          <svg style={{width: '100%', height: '100%'}} aria-label="Resonance Graph">
            <defs>
              <marker markerEnd="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="#41b3a3" />
              </marker>
            </defs>
            
            {/* Draw edges first (connections) */}
            {edges.map((edge, i) => (
              <line
                key={i}
                x1={edge.source.x}
                y1={edge.source.y}
                x2={edge.target.x}
                y2={edge.target.y}
                stroke={`rgba(65, 179, 163, ${edge.strength || 0.5})`}
                stroke-width={Math.max(1, (edge.strength || 0.5) * 4)}
                opacity={0.6}
              />
            ))}

            {/* Draw nodes second (on top) */}
            {nodes.map((node, i) => (
              <g key={i}>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={node.size || 15}
                  fill={node.color || '#e8a87c'}
                  stroke="#2b5c8f"
                  stroke-width={2}
                />
                <text
                  x={node.x}
                  y={node.y + 5}
                  textAnchor="middle"
                  fontSize={10}
                  fill="#fff"
                  style={{pointerEvents: 'none'}}
                >
                  {node.label || node.module || `Node ${i}`}
                </text>
              </g>
            ))}
          </svg>
        )}{
          !nodes || nodes.length === 0 && React.createElement('p', null, 'No module connections yet. Active modules will appear as you interact with the organism.')
        }
      </div>
      
      <div style={{marginTop: 12, fontSize: '0.8em', color: '#888'}}>
        <strong>Modules:</strong> {nodes.length} | 
        <strong>Connections:</strong> {edges.length} | 
        <strong>Avg Resonance:</strong> {(graphData.visual?.average_resonance || 0).toFixed(2)}
      </div>
    </div>
  );
};

export default ResonanceGraph;
