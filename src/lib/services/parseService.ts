import { prisma } from '../db';
import { ScriptParser } from '../parser/scriptParser';

export class ParseService {
  async parseAndSaveScript(scriptId: number): Promise<void> {
    // 获取剧本内容
    const script = await prisma.script.findUnique({
      where: { id: scriptId }
    });

    if (!script) {
      throw new Error('剧本不存在');
    }

    // 解析剧本
    const parser = new ScriptParser(script.content);
    const parsedScript = parser.parse();

    // 开始数据库事务
    await prisma.$transaction(async (tx) => {
      // 更新剧本标题和摘要
      await tx.script.update({
        where: { id: scriptId },
        data: {
          title: parsedScript.title || script.title,
          summary: parsedScript.scenes[0]?.content.slice(0, 200) + '...',
        }
      });

      // 保存场景信息
      for (const scene of parsedScript.scenes) {
        const savedScene = await tx.scene.create({
          data: {
            scriptId,
            name: scene.name,
            content: scene.content,
            location: scene.location,
            // 简单的场景强度计算
            intensity: this.calculateSceneIntensity(scene),
            // 简单的时长估算（基于内容长度）
            duration: Math.ceil(scene.content.length / 100)
          }
        });

        // 保存角色信息
        for (const charName of scene.characters) {
          const character = await tx.character.upsert({
            where: {
              scriptId_name: {
                scriptId,
                name: charName
              }
            },
            create: {
              scriptId,
              name: charName
            },
            update: {}
          });

          // 创建角色-场景关联
          await tx.characterScene.create({
            data: {
              characterId: character.id,
              sceneId: savedScene.id,
              dialogues: scene.dialogues.filter(d => d.character === charName).length
            }
          });
        }

        // 保存资源信息
        for (const resource of scene.resources) {
          const savedResource = await tx.resource.upsert({
            where: {
              scriptId_name: {
                scriptId,
                name: resource.name
              }
            },
            create: {
              scriptId,
              name: resource.name,
              type: resource.type
            },
            update: {
              type: resource.type
            }
          });

          // 创建资源-场景关联
          await tx.resourceScene.create({
            data: {
              resourceId: savedResource.id,
              sceneId: savedScene.id
            }
          });
        }
      }
    });
  }

  private calculateSceneIntensity(scene: { dialogues: any[]; content: string }): number {
    const factors = {
      dialogueCount: scene.dialogues.length * 0.1,
      exclamationMarks: (scene.content.match(/!/g) || []).length * 0.05,
      questionMarks: (scene.content.match(/\?/g) || []).length * 0.03,
      actionWords: (scene.content.match(/跑|跳|打|杀|爆|撞|追|逃/g) || []).length * 0.1
    };

    let intensity = Object.values(factors).reduce((sum, value) => sum + value, 0);
    return Math.min(Math.max(intensity, 0), 1); // 确保值在 0-1 之间
  }
} 