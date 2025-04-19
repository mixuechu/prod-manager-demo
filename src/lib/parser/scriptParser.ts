import { ParsedScript, ParsedScene, ResourceType, ResourceKeywords } from './types';

export class ScriptParser {
  private content: string;
  private lines: string[];
  private currentIndex: number = 0;

  constructor(content: string) {
    this.content = content;
    this.lines = content.split('\n').map(line => line.trim());
  }

  parse(): ParsedScript {
    const scenes: ParsedScene[] = [];
    const characters = new Map<string, { 
      description?: string;
      firstAppearance: number;
    }>();
    const resources = new Map<string, {
      type: ResourceType;
      description?: string;
    }>();

    // 解析场景
    while (this.currentIndex < this.lines.length) {
      const scene = this.parseScene();
      if (scene) {
        scenes.push(scene);
        
        // 收集角色信息
        scene.characters.forEach(char => {
          if (!characters.has(char)) {
            characters.set(char, {
              firstAppearance: scenes.length - 1
            });
          }
        });

        // 收集资源信息
        scene.resources.forEach(res => {
          if (!resources.has(res.name)) {
            resources.set(res.name, {
              type: res.type,
              description: res.description
            });
          }
        });
      }
    }

    return {
      title: this.parseTitle(),
      scenes,
      characters: Array.from(characters.entries()).map(([name, info]) => ({
        name,
        ...info
      })),
      resources: Array.from(resources.entries()).map(([name, info]) => ({
        name,
        ...info
      }))
    };
  }

  private parseTitle(): string {
    // 尝试从文件开头找到标题
    for (let i = 0; i < Math.min(5, this.lines.length); i++) {
      const line = this.lines[i];
      if (line && !line.startsWith('INT.') && !line.startsWith('EXT.')) {
        return line;
      }
    }
    return '未命名剧本';
  }

  private parseScene(): ParsedScene | null {
    // 跳过空行
    while (this.currentIndex < this.lines.length && !this.lines[this.currentIndex]) {
      this.currentIndex++;
    }

    if (this.currentIndex >= this.lines.length) {
      return null;
    }

    const sceneLine = this.lines[this.currentIndex];
    
    // 检查是否是场景标题（通常以 INT. 或 EXT. 开头）
    if (!sceneLine.startsWith('INT.') && !sceneLine.startsWith('EXT.')) {
      this.currentIndex++;
      return null;
    }

    const scene: ParsedScene = {
      name: sceneLine,
      content: '',
      characters: [],
      dialogues: [],
      resources: []
    };

    // 提取场景位置
    const locationMatch = sceneLine.match(/(?:INT\.|EXT\.)\s*(.*?)(?:\s*-\s*|$)/);
    if (locationMatch) {
      scene.location = locationMatch[1].trim();
      scene.resources.push({
        name: scene.location,
        type: 'location'
      });
    }

    this.currentIndex++;
    let sceneContent: string[] = [];
    
    // 解析场景内容直到下一个场景或文件结束
    while (this.currentIndex < this.lines.length) {
      const line = this.lines[this.currentIndex];
      
      // 检查是否到达下一个场景
      if (line.startsWith('INT.') || line.startsWith('EXT.')) {
        break;
      }

      // 解析对话
      if (this.isCharacterDialogue(line)) {
        const dialogue = this.parseDialogue();
        if (dialogue) {
          scene.dialogues.push(dialogue);
          if (!scene.characters.includes(dialogue.character)) {
            scene.characters.push(dialogue.character);
          }
          // 解析对话中的资源
          const dialogueResources = this.extractResources(dialogue.content);
          scene.resources.push(...dialogueResources);
        }
      }
      // 解析道具和资源
      else {
        const resources = this.extractResources(line);
        // 去重添加资源
        resources.forEach(resource => {
          if (!scene.resources.some(r => r.name === resource.name && r.type === resource.type)) {
            scene.resources.push(resource);
          }
        });
        sceneContent.push(line);
      }

      this.currentIndex++;
    }

    scene.content = sceneContent.join('\n');
    return scene;
  }

  private isCharacterDialogue(line: string): boolean {
    // 角色对话通常是全大写的角色名
    return /^[A-Z\s]+$/.test(line.trim());
  }

  private parseDialogue(): { character: string; content: string } | null {
    const character = this.lines[this.currentIndex].trim();
    this.currentIndex++;

    if (this.currentIndex >= this.lines.length) {
      return null;
    }

    let dialogueContent: string[] = [];
    while (this.currentIndex < this.lines.length) {
      const line = this.lines[this.currentIndex];
      if (!line || this.isCharacterDialogue(line) || line.startsWith('INT.') || line.startsWith('EXT.')) {
        break;
      }
      dialogueContent.push(line);
      this.currentIndex++;
    }

    this.currentIndex--; // 回退一行，因为主循环会再次递增
    return {
      character,
      content: dialogueContent.join('\n')
    };
  }

  private extractResources(line: string): Array<{ name: string; type: ResourceType; description?: string }> {
    const resources: Array<{ name: string; type: ResourceType; description?: string }> = [];
    
    // 提取括号中的内容作为道具或其他资源
    const bracketMatches = line.match(/[（(](.*?)[)）]/g);
    if (bracketMatches) {
      bracketMatches.forEach(match => {
        const content = match.slice(1, -1).trim();
        if (content) {
          const type = this.determineResourceType(content);
          resources.push({
            name: content,
            type,
            description: `从括号中提取: ${match}`
          });
        }
      });
    }

    // 根据关键词识别资源
    Object.entries(ResourceKeywords).forEach(([type, keywords]) => {
      keywords.forEach(keyword => {
        const regex = new RegExp(`${keyword}[\\s]*(.*?)(?=[。，；！？\\s]|$)`, 'g');
        let match;
        while ((match = regex.exec(line)) !== null) {
          if (match[1]?.trim()) {
            resources.push({
              name: match[1].trim(),
              type: type as ResourceType,
              description: `通过关键词"${keyword}"识别`
            });
          }
        }
      });
    });

    // 识别特定格式的资源描述
    const specialFormats = [
      { regex: /音效：(.*?)(?=[。，；！？\s]|$)/g, type: 'sound' },
      { regex: /音乐：(.*?)(?=[。，；！？\s]|$)/g, type: 'music' },
      { regex: /特效：(.*?)(?=[。，；！？\s]|$)/g, type: 'sfx' },
      { regex: /灯光：(.*?)(?=[。，；！？\s]|$)/g, type: 'lighting' }
    ];

    specialFormats.forEach(({ regex, type }) => {
      let match;
      while ((match = regex.exec(line)) !== null) {
        if (match[1]?.trim()) {
          resources.push({
            name: match[1].trim(),
            type: type as ResourceType,
            description: '特定格式标记'
          });
        }
      }
    });

    return resources;
  }

  private determineResourceType(content: string): ResourceType {
    // 根据内容特征判断资源类型
    const typePatterns: Record<ResourceType, RegExp[]> = {
      weapon: [/[枪刀剑斧矛弓箭炮]/, /武器/],
      vehicle: [/[车船机飞机火车自行车摩托]/, /交通工具/],
      tech: [/[手机电脑相机设备智能手表耳机充电器]/],
      costume: [/[衣服裙子外套帽子西装制服鞋子袜子围巾]/],
      makeup: [/[妆容发型口红眼影美妆眉毛睫毛粉底腮红]/],
      food: [/[食物饮料酒水果蔬菜点心主食零食汤茶]/],
      animal: [/[狗猫鸟马牛羊鱼兔子老虎狮子大象蛇]/],
      sound: [/[声音响声噪音回声嘈杂寂静轰鸣尖叫低语]/],
      music: [/[音乐歌曲旋律节奏BGM背景音乐和声乐器交响乐]/i],
      sfx: [/[特效爆炸火焰烟雾闪电魔法效果粒子光效水花震动]/],
      lighting: [/[灯光照明阴影明暗日光月光霓虹闪烁投影]/],
      set: [/[布景装饰家具墙壁地板天花板窗户门]/],
      accessory: [/[项链手表戒指耳环手链胸针帽子眼镜腰带包包]/],
      weather: [/[晴天雨天阴天雪天大风雾霾雷电冰雹彩虹云彩]/, /天气/],
      time: [/[早晨中午下午傍晚晚上凌晨黎明黄昏午夜日出]/, /时间/],
      gesture: [/[微笑皱眉挥手点头摇头耸肩鼓掌握手拥抱跳跃]/, /动作/, /姿势/],
      emotion: [/[开心悲伤愤怒惊讶恐惧厌恶期待焦虑平静兴奋]/, /情绪/, /表情/],
      prop: [/.+/], // 默认作为道具
      location: [], // 通过其他方式识别
      other: []
    };

    // 首先检查特定格式标记
    const specialFormats = {
      weather: /天气[：:]/,
      time: /时间[：:]/,
      gesture: /动作[：:]/,
      emotion: /情绪[：:]/,
      accessory: /配饰[：:]/
    };

    for (const [type, pattern] of Object.entries(specialFormats)) {
      if (pattern.test(content)) {
        return type as ResourceType;
      }
    }

    // 然后检查详细的类型模式
    for (const [type, patterns] of Object.entries(typePatterns)) {
      if (patterns.some(pattern => pattern.test(content))) {
        return type as ResourceType;
      }
    }

    return 'other';
  }
} 