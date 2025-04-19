import React from 'react';
import Link from 'next/link';

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link href="/" className="text-xl font-bold text-primary">
                  剧本管理系统
                </Link>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link href="/scripts" className="inline-flex items-center px-1 pt-1 text-gray-900 hover:text-primary">
                  剧本列表
                </Link>
                <Link href="/statistics" className="inline-flex items-center px-1 pt-1 text-gray-900 hover:text-primary">
                  统计分析
                </Link>
                <Link href="/resources" className="inline-flex items-center px-1 pt-1 text-gray-900 hover:text-primary">
                  资源管理
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <button className="bg-primary text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-600">
                新建剧本
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-500 text-sm">
            © 2024 剧本管理系统. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
} 