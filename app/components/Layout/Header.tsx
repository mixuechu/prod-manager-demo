'use client';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export default function Header({ title, subtitle }: HeaderProps) {
  return (
    <div className="border-b border-gray-200 pb-4 mb-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
        <div className="flex gap-2">
          <button className="btn btn-outline-secondary btn-sm">
            导出PDF
          </button>
          <button className="btn btn-outline-secondary btn-sm">
            分享
          </button>
          <button className="btn btn-primary btn-sm">
            <i className="mdi mdi-autorenew mr-1"></i>
            重新生成
          </button>
        </div>
      </div>
    </div>
  );
} 