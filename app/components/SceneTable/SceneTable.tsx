'use client';

import React from 'react';

interface Scene {
  id: string;
  page: string;
  summary: string;
  mainActors: string[];
  specialRequirements: string;
  status: 'pending' | 'completed' | 'in_progress';
}

interface SceneTableProps {
  scenes: Scene[];
}

export default function SceneTable({ scenes }: SceneTableProps) {
  const getStatusBadge = (status: Scene['status']) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            已完成
          </span>
        );
      case 'in_progress':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            进行中
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            待拍摄
          </span>
        );
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              场景
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              页数
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              内容概要
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              主要演员
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              特殊需求
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              状态
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {scenes.map((scene) => (
            <tr key={scene.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {scene.id}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {scene.page}
              </td>
              <td className="px-6 py-4 text-sm text-gray-900">
                {scene.summary}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {scene.mainActors.join(', ')}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {scene.specialRequirements}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {getStatusBadge(scene.status)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-4 flex justify-between items-center">
        <div className="text-sm text-gray-500">
          共 {scenes.length} 个场景
        </div>
        <div className="flex gap-2">
          <button className="btn btn-outline-secondary btn-sm">
            <i className="mdi mdi-file-export-outline mr-1"></i>
            导出顺场表
          </button>
          <button className="btn btn-primary btn-sm">
            <i className="mdi mdi-plus mr-1"></i>
            添加场景
          </button>
        </div>
      </div>
    </div>
  );
} 