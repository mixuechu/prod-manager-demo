import { writeFile } from 'fs/promises';
import { join } from 'path';
import { mkdir } from 'fs/promises';

export async function saveUploadedFile(
  file: File,
  directory: string = 'uploads'
): Promise<string> {
  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);

  // 确保上传目录存在
  const uploadDir = join(process.cwd(), 'public', directory);
  await mkdir(uploadDir, { recursive: true });

  // 生成唯一文件名
  const uniqueSuffix = `${Date.now()}-${Math.round(Math.random() * 1E9)}`;
  const filename = `${file.name.split('.')[0]}-${uniqueSuffix}.${file.name.split('.').pop()}`;
  const filepath = join(directory, filename);
  const fullPath = join(process.cwd(), 'public', filepath);

  // 保存文件
  await writeFile(fullPath, buffer);

  // 返回相对路径
  return filepath;
} 