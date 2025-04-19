import { NextResponse } from 'next/server';
import { prisma } from '@/lib/db';

interface RouteParams {
  params: {
    id: string;
  };
}

export async function DELETE(request: Request, { params }: RouteParams) {
  try {
    const id = parseInt(params.id);

    if (isNaN(id)) {
      return NextResponse.json(
        { error: '无效的剧本ID' },
        { status: 400 }
      );
    }

    // 删除剧本及其关联数据
    await prisma.script.delete({
      where: { id },
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Delete script error:', error);
    return NextResponse.json(
      { error: '删除剧本失败' },
      { status: 500 }
    );
  }
}

export async function GET(request: Request, { params }: RouteParams) {
  try {
    const id = parseInt(params.id);

    if (isNaN(id)) {
      return NextResponse.json(
        { error: '无效的剧本ID' },
        { status: 400 }
      );
    }

    const script = await prisma.script.findUnique({
      where: { id },
      include: {
        scenes: true,
        characters: true,
        resources: true,
        comments: true,
      },
    });

    if (!script) {
      return NextResponse.json(
        { error: '剧本不存在' },
        { status: 404 }
      );
    }

    return NextResponse.json(script);
  } catch (error) {
    console.error('Fetch script error:', error);
    return NextResponse.json(
      { error: '获取剧本详情失败' },
      { status: 500 }
    );
  }
} 