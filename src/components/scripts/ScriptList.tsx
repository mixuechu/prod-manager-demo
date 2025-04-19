import React from 'react';
import Link from 'next/link';
import { ScriptCard } from './ScriptCard';

interface Script {
  id: number;
  title: string;
  author: string;
  updatedAt: string;
  status: 'draft' | 'reviewing' | 'published';
  coverImage?: string;
  summary?: string;
}

export function ScriptList() {
  const [scripts, setScripts] = React.useState<Script[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    fetchScripts();
  }, []);

  const fetchScripts = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/scripts');
      if (!response.ok) {
        throw new Error('Failed to fetch scripts');
      }
      const data = await response.json();
      setScripts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取剧本列表失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
        <p className="mt-4 text-gray-500">加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-500">{error}</p>
        <button
          onClick={() => fetchScripts()}
          className="mt-4 text-primary hover:text-blue-600"
        >
          重试
        </button>
      </div>
    );
  }

  if (scripts.length === 0) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-500">暂无剧本</p>
        <Link
          href="/scripts/new"
          className="mt-4 inline-block text-primary hover:text-blue-600"
        >
          创建新剧本
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      {scripts.map((script) => (
        <ScriptCard key={script.id} script={script} onUpdate={fetchScripts} />
      ))}
    </div>
  );
} 