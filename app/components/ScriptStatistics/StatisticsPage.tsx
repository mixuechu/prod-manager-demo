import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import { NetworkGraph } from './NetworkGraph';
import { HeatMap } from './HeatMap';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface StatisticsData {
  scene_statistics: {
    duration_distribution: ChartData;
    scene_types: ChartData;
    location_frequency: ChartData;
    intensity_distribution: ChartData;
  };
  character_statistics: {
    appearance_frequency: ChartData;
    dialogue_distribution: ChartData;
    interaction_network: NetworkData;
    emotion_trends: ChartData;
  };
  resource_statistics: {
    type_distribution: ChartData;
    usage_heatmap: HeatMapData;
    complexity_distribution: ChartData;
    resource_correlations: NetworkData;
  };
  timeline_statistics: {
    timeline_distribution: ChartData;
    plot_development: ChartData;
    transition_frequency: ChartData;
    pacing_changes: ChartData;
  };
}

interface ChartData {
  labels: string[];
  data: number[];
  type: 'bar' | 'line' | 'pie';
  title: string;
}

interface NetworkData {
  nodes: Array<{ id: string; name: string }>;
  edges: Array<{ source: string; target: string; value: number }>;
  type: 'network';
  title: string;
}

interface HeatMapData {
  data: number[][];
  type: 'heatmap';
  title: string;
}

export function StatisticsPage() {
  const router = useRouter();
  const { scriptId } = router.query;
  const [statistics, setStatistics] = useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (scriptId) {
      fetchStatistics();
    }
  }, [scriptId]);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/statistics/scripts/${scriptId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch statistics');
      }
      const data = await response.json();
      setStatistics(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading statistics...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center">{error}</div>;
  }

  if (!statistics) {
    return <div>No statistics available</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Script Statistics</h1>
      
      {/* Scene Statistics */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-6">Scene Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <Bar
              data={{
                labels: statistics.scene_statistics.duration_distribution.labels,
                datasets: [{
                  label: 'Scene Duration Distribution',
                  data: statistics.scene_statistics.duration_distribution.data,
                  backgroundColor: 'rgba(54, 162, 235, 0.5)',
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.scene_statistics.duration_distribution.title,
                  },
                },
              }}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <Pie
              data={{
                labels: statistics.scene_statistics.scene_types.labels,
                datasets: [{
                  data: statistics.scene_statistics.scene_types.data,
                  backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                  ],
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.scene_statistics.scene_types.title,
                  },
                },
              }}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <Bar
              data={{
                labels: statistics.scene_statistics.location_frequency.labels,
                datasets: [{
                  label: 'Location Frequency',
                  data: statistics.scene_statistics.location_frequency.data,
                  backgroundColor: 'rgba(75, 192, 192, 0.5)',
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.scene_statistics.location_frequency.title,
                  },
                },
              }}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <Line
              data={{
                labels: statistics.scene_statistics.intensity_distribution.labels,
                datasets: [{
                  label: 'Scene Intensity',
                  data: statistics.scene_statistics.intensity_distribution.data,
                  borderColor: 'rgba(153, 102, 255, 1)',
                  tension: 0.1,
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.scene_statistics.intensity_distribution.title,
                  },
                },
              }}
            />
          </div>
        </div>
      </section>

      {/* Character Statistics */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-6">Character Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <Bar
              data={{
                labels: statistics.character_statistics.appearance_frequency.labels,
                datasets: [{
                  label: 'Character Appearances',
                  data: statistics.character_statistics.appearance_frequency.data,
                  backgroundColor: 'rgba(255, 159, 64, 0.5)',
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.character_statistics.appearance_frequency.title,
                  },
                },
              }}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <Pie
              data={{
                labels: statistics.character_statistics.dialogue_distribution.labels,
                datasets: [{
                  data: statistics.character_statistics.dialogue_distribution.data,
                  backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)',
                  ],
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.character_statistics.dialogue_distribution.title,
                  },
                },
              }}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow col-span-2">
            <NetworkGraph
              data={statistics.character_statistics.interaction_network}
              width={800}
              height={400}
            />
          </div>
        </div>
      </section>

      {/* Resource Statistics */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-6">Resource Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <Pie
              data={{
                labels: statistics.resource_statistics.type_distribution.labels,
                datasets: [{
                  data: statistics.resource_statistics.type_distribution.data,
                  backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                  ],
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.resource_statistics.type_distribution.title,
                  },
                },
              }}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <HeatMap
              data={statistics.resource_statistics.usage_heatmap}
              width={400}
              height={300}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow col-span-2">
            <NetworkGraph
              data={statistics.resource_statistics.resource_correlations}
              width={800}
              height={400}
            />
          </div>
        </div>
      </section>

      {/* Timeline Statistics */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-6">Timeline Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <Bar
              data={{
                labels: statistics.timeline_statistics.timeline_distribution.labels,
                datasets: [{
                  label: 'Timeline Distribution',
                  data: statistics.timeline_statistics.timeline_distribution.data,
                  backgroundColor: 'rgba(255, 99, 132, 0.5)',
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.timeline_statistics.timeline_distribution.title,
                  },
                },
              }}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <Line
              data={{
                labels: statistics.timeline_statistics.plot_development.labels,
                datasets: [{
                  label: 'Plot Development',
                  data: statistics.timeline_statistics.plot_development.data,
                  borderColor: 'rgba(54, 162, 235, 1)',
                  tension: 0.1,
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.timeline_statistics.plot_development.title,
                  },
                },
              }}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <Bar
              data={{
                labels: statistics.timeline_statistics.transition_frequency.labels,
                datasets: [{
                  label: 'Transition Types',
                  data: statistics.timeline_statistics.transition_frequency.data,
                  backgroundColor: 'rgba(75, 192, 192, 0.5)',
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.timeline_statistics.transition_frequency.title,
                  },
                },
              }}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <Line
              data={{
                labels: statistics.timeline_statistics.pacing_changes.labels,
                datasets: [{
                  label: 'Pacing Changes',
                  data: statistics.timeline_statistics.pacing_changes.data,
                  borderColor: 'rgba(153, 102, 255, 1)',
                  tension: 0.1,
                }],
              }}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: statistics.timeline_statistics.pacing_changes.title,
                  },
                },
              }}
            />
          </div>
        </div>
      </section>
    </div>
  );
} 