'use client';

import React, { useState } from 'react';
import MainLayout from './components/Layout/MainLayout';
import Header from './components/Layout/Header';
import ScriptUpload from './components/ScriptUpload/ScriptUpload';
import ResourceTable from './components/ResourceTable/ResourceTable';
import SceneTable from './components/SceneTable/SceneTable';

// 示例数据
const mockResources = [
  {
    type: '服装' as const,
    element: '红色礼服',
    scenes: ['S1', 'S3'],
    notes: '需准备2套备用'
  },
  {
    type: '道具' as const,
    element: '古董怀表',
    scenes: ['S2'],
    notes: '需提前3天租赁'
  },
  {
    type: '场景' as const,
    element: '医院走廊',
    scenes: ['S5', 'S6', 'S7'],
    notes: '需夜间拍摄许可'
  }
];

const mockScenes = [
  {
    id: 'S1',
    page: '1.2',
    summary: '客厅争吵戏',
    mainActors: ['张三', '李四'],
    specialRequirements: '需要雨声效果',
    status: 'completed' as const
  },
  {
    id: 'S3',
    page: '4.5',
    summary: '医院重逢',
    mainActors: ['王五', '赵六'],
    specialRequirements: '需轮椅道具',
    status: 'pending' as const
  }
];

export default function Home() {
  const [activeTab, setActiveTab] = useState('graph');

  const handleFileUpload = (file: File) => {
    console.log('Uploaded file:', file);
    // TODO: 处理文件上传
  };

  return (
    <MainLayout>
      <Header 
        title="《消失的时间》剧本分析"
        subtitle="已成功解析剧本《消失的时间_v3.fdx》，共28场戏，12个角色"
      />
      
      <div className="mb-8">
        <ScriptUpload onUpload={handleFileUpload} />
      </div>

      <div className="mb-6">
        <nav className="flex space-x-4" aria-label="Tabs">
          {[
            { id: 'graph', name: '故事图谱', icon: 'mdi-graph' },
            { id: 'resources', name: '资源表格', icon: 'mdi-table' },
            { id: 'scenes', name: '顺场表', icon: 'mdi-script-text' },
            { id: 'schedule', name: '拍摄排期', icon: 'mdi-calendar' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                activeTab === tab.id
                  ? 'bg-primary text-white'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <i className={`mdi ${tab.icon} mr-2`}></i>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6">
        {activeTab === 'graph' && (
          <div className="h-[600px] flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-gray-500">故事图谱可视化区域</p>
          </div>
        )}

        {activeTab === 'resources' && (
          <ResourceTable resources={mockResources} />
        )}

        {activeTab === 'scenes' && (
          <SceneTable scenes={mockScenes} />
        )}

        {activeTab === 'schedule' && (
          <div className="h-[600px] flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-gray-500">拍摄排期日历区域</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
