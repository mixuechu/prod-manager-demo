import React from 'react';
import dynamic from 'next/dynamic';

// Dynamically import ForceGraph2D to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
});

interface NetworkGraphProps {
  data: {
    nodes: Array<{ id: string; name: string }>;
    edges: Array<{ source: string; target: string; value: number }>;
    type: 'network';
    title: string;
  };
  width: number;
  height: number;
}

export function NetworkGraph({ data, width, height }: NetworkGraphProps) {
  // Transform edges array to match ForceGraph2D's link format
  const graphData = {
    nodes: data.nodes,
    links: data.edges.map(edge => ({
      source: edge.source,
      target: edge.target,
      value: edge.value,
    })),
  };

  return (
    <div className="relative">
      <h3 className="text-lg font-semibold mb-4 text-center">{data.title}</h3>
      <div className="border rounded-lg overflow-hidden">
        <ForceGraph2D
          graphData={graphData}
          width={width}
          height={height}
          nodeLabel="name"
          nodeColor={() => '#4299E1'} // Blue color for nodes
          linkColor={() => '#A0AEC0'} // Gray color for links
          linkWidth={link => (link.value as number) * 2} // Scale link width based on value
          nodeRelSize={8} // Size of nodes
          linkDirectionalParticles={2} // Add particles to show direction
          linkDirectionalParticleSpeed={d => d.value * 0.001} // Particle speed based on value
          cooldownTicks={50} // Reduce simulation time
          onEngineStop={() => {}} // Optional: Add callback when simulation stops
        />
      </div>
    </div>
  );
} 