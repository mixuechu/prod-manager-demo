export interface ParsedScene {
  name: string;
  content: string;
  location?: string;
  characters: string[];
  dialogues: Array<{
    character: string;
    content: string;
  }>;
  resources: Array<{
    name: string;
    type: ResourceType;
    description?: string;
  }>;
}

export interface ParsedScript {
  title: string;
  scenes: ParsedScene[];
  characters: Array<{
    name: string;
    description?: string;
    firstAppearance: number; // 首次出现的场景索引
  }>;
  resources: Array<{
    name: string;
    type: ResourceType;
    description?: string;
  }>;
}

export type ResourceType = 
  | 'prop'        // 道具
  | 'location'    // 场景位置
  | 'costume'     // 服装
  | 'makeup'      // 化妆/妆容
  | 'sound'       // 音效
  | 'music'       // 音乐
  | 'sfx'         // 特效
  | 'lighting'    // 灯光
  | 'vehicle'     // 交通工具
  | 'weapon'      // 武器
  | 'animal'      // 动物
  | 'food'        // 食物饮品
  | 'tech'        // 科技设备
  | 'set'         // 布景
  | 'accessory'   // 配饰
  | 'weather'     // 天气
  | 'time'        // 时间
  | 'gesture'     // 动作姿势
  | 'emotion'     // 情绪表现
  | 'other';      // 其他

// 资源关键词映射
export const ResourceKeywords: Record<ResourceType, string[]> = {
  prop: ['拿着', '手持', '放在', '摆放', '使用', '把玩', '抓住', '捡起', '扔掉'],
  location: ['在', '到', '向', '从', '穿过', '经过', '位于', '停留', '抵达', '离开'],
  costume: ['穿着', '戴着', '披着', '换装', '衣服', '裙子', '西装', '制服', '外套', '鞋子', '袜子', '围巾'],
  makeup: ['妆容', '化妆', '口红', '眼影', '发型', '美妆', '眉毛', '睫毛', '粉底', '腮红'],
  sound: ['响起', '传来', '声音', '噪音', '回声', '嘈杂', '寂静', '轰鸣', '尖叫', '低语'],
  music: ['音乐', '歌曲', '旋律', '节奏', 'BGM', '背景音乐', '和声', '乐器', '交响乐', '主题曲'],
  sfx: ['特效', '爆炸', '火焰', '烟雾', '闪电', '魔法效果', '粒子', '光效', '水花', '震动'],
  lighting: ['灯光', '照明', '聚光灯', '阴影', '明暗', '日光', '月光', '霓虹', '闪烁', '投影'],
  vehicle: ['车', '自行车', '摩托', '飞机', '船', '火车', '电瓶车', '公交车', '出租车', '地铁'],
  weapon: ['枪', '刀', '剑', '弓箭', '武器', '手枪', '步枪', '长矛', '盾牌', '炸弹'],
  animal: ['狗', '猫', '马', '鸟', '鱼', '兔子', '老虎', '狮子', '大象', '蛇'],
  food: ['食物', '饮料', '酒', '菜', '水果', '点心', '主食', '零食', '汤', '茶'],
  tech: ['手机', '电脑', '平板', '设备', '机器', '智能手表', '耳机', '充电器', '投影仪', '摄像机'],
  set: ['布景', '场景', '装饰', '陈设', '家具', '墙壁', '地板', '天花板', '窗户', '门'],
  accessory: ['项链', '手表', '戒指', '耳环', '手链', '胸针', '帽子', '眼镜', '腰带', '包包'],
  weather: ['晴天', '雨天', '阴天', '雪天', '大风', '雾霾', '雷电', '冰雹', '彩虹', '云彩'],
  time: ['早晨', '中午', '下午', '傍晚', '晚上', '凌晨', '黎明', '黄昏', '午夜', '日出'],
  gesture: ['微笑', '皱眉', '挥手', '点头', '摇头', '耸肩', '鼓掌', '握手', '拥抱', '跳跃'],
  emotion: ['开心', '悲伤', '愤怒', '惊讶', '恐惧', '厌恶', '期待', '焦虑', '平静', '兴奋'],
  other: []
}; 