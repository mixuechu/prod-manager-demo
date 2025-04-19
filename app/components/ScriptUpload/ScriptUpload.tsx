'use client';

import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface ScriptUploadProps {
  onUpload: (file: File) => void;
}

export default function ScriptUpload({ onUpload }: ScriptUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt', '.fountain'],
      'application/x-final-draft': ['.fdx']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setIsUploading(true);
        // 模拟上传进度
        let progress = 0;
        const interval = setInterval(() => {
          progress += 10;
          setUploadProgress(progress);
          if (progress >= 100) {
            clearInterval(interval);
            setIsUploading(false);
            onUpload(acceptedFiles[0]);
          }
        }, 200);
      }
    }
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-primary'}`}
      >
        <input {...getInputProps()} />
        <i className="mdi mdi-file-upload text-4xl text-gray-400 mb-4"></i>
        <div className="text-gray-600">
          {isDragActive ? (
            <p>将文件拖放到此处</p>
          ) : (
            <>
              <p className="font-medium">点击上传或拖放文件</p>
              <p className="text-sm mt-1">
                支持 PDF、Word、Final Draft、Fountain 格式
              </p>
            </>
          )}
        </div>
      </div>

      {isUploading && (
        <div className="mt-4">
          <div className="flex justify-between text-sm mb-1">
            <span>上传进度</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full">
            <div
              className="h-2 bg-primary rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-500">
        <p>
          <i className="mdi mdi-information-outline mr-1"></i>
          上传后，AI 将自动解析剧本并生成：
        </p>
        <ul className="list-disc list-inside mt-2 space-y-1 ml-4">
          <li>可视化故事图谱</li>
          <li>服化道资源表格</li>
          <li>专业顺场表</li>
          <li>智能拍摄排期</li>
        </ul>
      </div>
    </div>
  );
} 