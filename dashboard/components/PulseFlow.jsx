import React, { useEffect, useState, useRef } from 'react';

const PulseFlow = ({nodes, edges, width, height}) => {
  const [flowPositions, setFlowPositions] = useState([]);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!nodes || nodes.length === 0) {
      setFlowPositions([]);
      return;
    }

    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;

    // Initialize positions if not set
    if (flowPositions.length === 0) {
      const positions = nodes.map(() => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
      }));
      setFlowPositions(positions);
    }

    // Animation loop
    const animate = () => {
      const positions = [...flowPositions];
      
      // Update positions with simple physics
      positions.forEach((pos, i) => {
        // Apply velocity
        pos.x += pos.vx;
        pos.y += pos.vy;
        
        // Bounce off walls
        if (pos.x < 0 || pos.x > width) pos.vx *= -1;
        if (pos.y < 0 || pos.y > height) pos.vy *= -1;
        
        // Keep within bounds
        pos.x = Math.max(0, Math.min(width, pos.x));
        pos.y = Math.max(0, Math.min(height, pos.y));
      });

      setFlowPositions(positions);
      
      // Clear and redraw
      ctx.clearRect(0, 0, width, height);
      
      // Draw connections
      edges?.forEach(edge => {
        const source = positions.find(n => n.id === edge.source.id);
        const target = positions.find(n => n.id === edge.target.id);
        if (source && target) {
          ctx.beginPath();
          ctx.moveTo(source.x, source.y);
          ctx.lineTo(target.x, target.y);
          const strength = edge.strength || 0.5;
          ctx.strokeStyle = `rgba(65, 179, 163, ${strength * 0.5})`;
          ctx.lineWidth = Math.max(1, strength * 3);
          ctx.stroke();
        }
      });

      // Draw nodes
      nodes.forEach((node, i) => {
        const pos = positions[i];
        if (!pos) return;
        
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = '#2b5c8f';
        ctx.fill();
        ctx.strokeStyle = '#41b3a3';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Label
        ctx.fillStyle = '#fff';
        ctx.font = '10px Segoe UI';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(node.label || `M${i}`, pos.x, pos.y);
      });
    };

    // Initial draw
    animate();
    
    // Continuous animation
    const interval = setInterval(animate, 100);
    return () => clearInterval(interval);
  }, [nodes, edges, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{position: 'absolute', top: 0, left: 0}}
    />
  );
};

export default PulseFlow;
