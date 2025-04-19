import React from 'react';
import HeatMapGrid from 'react-heatmap-grid';

interface HeatMapProps {
  data: {
    xLabels: string[];
    yLabels: string[];
    data: number[][];
    title: string;
  };
  width: number;
  height: number;
}

export function HeatMap({ data, width, height }: HeatMapProps) {
  // Calculate cell size based on container dimensions and label counts
  const cellHeight = Math.floor((height - 60) / data.yLabels.length);
  const cellWidth = Math.floor((width - 100) / data.xLabels.length);

  return (
    <div className="relative" style={{ width, height }}>
      <h3 className="text-lg font-semibold mb-4 text-center">{data.title}</h3>
      <div className="border rounded-lg p-4">
        <HeatMapGrid
          xLabels={data.xLabels}
          yLabels={data.yLabels}
          data={data.data}
          cellStyle={(_background: string, value: number, min: number, max: number) => ({
            background: `rgb(66, 153, 225, ${(value - min) / (max - min)})`,
            fontSize: '11px',
            color: value > (max - min) / 2 ? '#fff' : '#444',
            padding: '6px',
            height: `${cellHeight}px`,
            width: `${cellWidth}px`,
          })}
          cellRender={(value: number) => value.toFixed(2)}
          xLabelsStyle={() => ({
            fontSize: '12px',
            textTransform: 'uppercase',
            color: '#666',
            paddingBottom: '5px',
          })}
          yLabelsStyle={() => ({
            fontSize: '12px',
            textTransform: 'uppercase',
            color: '#666',
            paddingRight: '10px',
          })}
        />
      </div>
    </div>
  );
} 