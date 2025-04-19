import { ScriptList } from '@/components/scripts/ScriptList';
import { UploadButton } from '@/components/scripts/UploadButton';

export default function ScriptsPage() {
  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">剧本管理</h1>
        <UploadButton />
      </div>
      
      <div className="bg-white shadow rounded-lg">
        <ScriptList />
      </div>
    </div>
  );
} 