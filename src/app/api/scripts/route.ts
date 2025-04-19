import { NextResponse } from 'next/server';
import { prisma } from '@/lib/db';

export async function GET() {
  try {
    const scripts = await prisma.script.findMany({
      orderBy: {
        updatedAt: 'desc',
      },
      select: {
        id: true,
        title: true,
        author: true,
        summary: true,
        status: true,
        coverImage: true,
        updatedAt: true,
        _count: {
          select: {
            scenes: true,
            characters: true,
            resources: true,
          },
        },
      },
    });

    return NextResponse.json(scripts);
  } catch (error) {
    console.error('Fetch scripts error:', error);
    return NextResponse.json(
      { error: '获取剧本列表失败' },
      { status: 500 }
    );
  }
} 