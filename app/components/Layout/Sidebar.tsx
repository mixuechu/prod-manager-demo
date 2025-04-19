'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavItem {
  href: string;
  icon: string;
  label: string;
}

const navItems: NavItem[] = [
  { href: '/', icon: 'mdi-home', label: '项目概览' },
  { href: '/script', icon: 'mdi-script-text', label: '剧本分析' },
  { href: '/characters', icon: 'mdi-account-group', label: '角色管理' },
  { href: '/costumes', icon: 'mdi-tshirt-crew', label: '服装道具' },
  { href: '/schedule', icon: 'mdi-calendar-clock', label: '拍摄排期' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [currentProject, setCurrentProject] = useState('《消失的时间》电影版');

  return (
    <div className="fixed h-screen w-72 bg-gradient-to-b from-gray-800 to-gray-900 text-white p-6">
      <div className="flex justify-between items-center mb-8">
        <h4 className="text-xl font-semibold">
          <i className="mdi mdi-movie-roll"></i> 制片助手
        </h4>
      </div>
      
      <nav>
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                  pathname === item.href
                    ? 'bg-primary text-white'
                    : 'text-gray-300 hover:bg-primary/80 hover:text-white'
                }`}
              >
                <i className={`mdi ${item.icon} mr-3`}></i>
                {item.label}
              </Link>
            </li>
          ))}
          <li className="mt-8">
            <Link
              href="/ai"
              className="flex items-center px-4 py-2 rounded-lg text-yellow-400 hover:bg-yellow-400/20"
            >
              <i className="mdi mdi-lightning-bolt mr-3"></i>
              AI智能生成
            </Link>
          </li>
        </ul>
      </nav>

      <div className="absolute bottom-6 left-6 right-6">
        <div className="bg-gray-900 rounded-lg p-4">
          <h6 className="mb-2">当前项目</h6>
          <select
            value={currentProject}
            onChange={(e) => setCurrentProject(e.target.value)}
            className="w-full bg-gray-800 text-white border-gray-700 rounded-md mb-2"
          >
            <option>《消失的时间》电影版</option>
            <option>《夏日回忆》广告片</option>
          </select>
          <button className="w-full btn btn-primary btn-sm">
            + 新建项目
          </button>
        </div>
      </div>
    </div>
  );
} 