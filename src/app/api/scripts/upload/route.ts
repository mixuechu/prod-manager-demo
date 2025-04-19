import { NextResponse } from 'next/server';
import { prisma } from '@/lib/db';
import { saveUploadedFile } from '@/lib/upload';
import { ParseService } from '@/lib/services/parseService';

const parseService = new ParseService();

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { error: '未找到上传的文件' },
        { status: 400 }
      );
    }

    // 保存文件
    const filepath = await saveUploadedFile(file, 'scripts');

    // 读取文件内容
    const content = await file.text();

    // 创建剧本记录
    const script = await prisma.script.create({
      data: {
        title: file.name.split('.')[0], // 使用文件名作为临时标题
        author: 'Unknown', // 后续可以从用户会话中获取
        content: content,
        status: 'draft',
      },
    });

    // 解析剧本内容
    try {
      await parseService.parseAndSaveScript(script.id);
    } catch (parseError) {
      console.error('Parse error:', parseError);
      // 即使解析失败，也返回创建的剧本
    }

    // 获取更新后的剧本信息
    const updatedScript = await prisma.script.findUnique({
      where: { id: script.id },
      include: {
        _count: {
          select: {
            scenes: true,
            characters: true,
            resources: true,
          },
        },
      },
    });

    return NextResponse.json(updatedScript);
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: '上传失败' },
      { status: 500 }
    );
  }
} 