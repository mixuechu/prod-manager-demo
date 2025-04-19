import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

interface Script {
  id: number;
  title: string;
  author: string;
  updatedAt: string;
  status: 'draft' | 'reviewing' | 'published';
  coverImage?: string;
  summary?: string;
}

interface ScriptCardProps {
  script: Script;
  onUpdate: () => void;
}

export function ScriptCard({ script, onUpdate }: ScriptCardProps) {
  const statusColors = {
    draft: 'bg-gray-100 text-gray-800',
    reviewing: 'bg-yellow-100 text-yellow-800',
    published: 'bg-green-100 text-green-800',
  };

  const statusText = {
    draft: '草稿',
    reviewing: '审核中',
    published: '已发布',
  };

  const handleDelete = async () => {
    if (!confirm('确定要删除这个剧本吗？')) {
      return;
    }

    try {
      const response = await fetch(`/api/scripts/${script.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('删除失败');
      }

      onUpdate();
    } catch (error) {
      alert('删除剧本时出错');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="relative h-48">
        {script.coverImage ? (
          <Image
            src={script.coverImage}
            alt={script.title}
            fill
            className="object-cover"
          />
        ) : (
          <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
            <span className="text-gray-400">暂无封面</span>
          </div>
        )}
      </div>

      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <Link 
            href={`/scripts/${script.id}`}
            className="text-lg font-semibold text-gray-900 hover:text-primary"
          >
            {script.title}
          </Link>
          <span className={`px-2 py-1 rounded-full text-xs ${statusColors[script.status]}`}>
            {statusText[script.status]}
          </span>
        </div>

        <p className="text-sm text-gray-500 mb-4">
          作者: {script.author}
        </p>

        {script.summary && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {script.summary}
          </p>
        )}

        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-500">
            更新于 {new Date(script.updatedAt).toLocaleDateString()}
          </span>
          
          <div className="space-x-2">
            <Link
              href={`/scripts/${script.id}/edit`}
              className="text-primary hover:text-blue-600"
            >
              编辑
            </Link>
            <button
              onClick={handleDelete}
              className="text-red-600 hover:text-red-700"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 