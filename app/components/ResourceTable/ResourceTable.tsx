'use client';

import React from 'react';

interface Resource {
  type: '服装' | '道具' | '场景';
  element: string;
  scenes: string[];
  notes: string;
}

interface ResourceTableProps {
  resources: Resource[];
}

export default function ResourceTable({ resources }: ResourceTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              类型
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              元素
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              出现场次
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              备注
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              操作
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {resources.map((resource, index) => (
            <tr key={index} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                  ${resource.type === '服装' ? 'bg-blue-100 text-blue-800' :
                    resource.type === '道具' ? 'bg-green-100 text-green-800' :
                    'bg-purple-100 text-purple-800'
                  }`}
                >
                  {resource.type}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {resource.element}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {resource.scenes.join(', ')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {resource.notes}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <button className="text-primary hover:text-primary-dark mr-3">
                  <i className="mdi mdi-pencil"></i>
                </button>
                <button className="text-red-600 hover:text-red-800">
                  <i className="mdi mdi-delete"></i>
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-4 flex justify-end">
        <button className="btn btn-primary btn-sm">
          <i className="mdi mdi-plus mr-1"></i>
          添加资源
        </button>
      </div>
    </div>
  );
} 