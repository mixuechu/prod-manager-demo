以下是为制片管理系统设计的RESTful API接口文档，涵盖前后端交互的所有核心端点，采用OpenAPI 3.0规范格式：

```markdown
# 制片管理平台 API 文档

## 基础信息
- **Base URL**: `/api/v1`
- **认证方式**: JWT (除标注外所有端点需认证)
- **响应格式**: JSON

## 1. 剧本管理
### 1.1 上传剧本
```http
POST /scripts
```
**请求格式**: `multipart/form-data`  
**字段**:
- `file`: 剧本文件（支持.txt/.pdf/.fdx）
- `project_id`: 关联项目ID（可选）

**成功响应**:
```json
{
  "id": "script_123",
  "filename": "剧本.pdf",
  "status": "parsing",
  "metadata": {
    "page_count": 42,
    "characters_count": 15
  }
}
```

### 1.2 获取解析结果
```http
GET /scripts/{script_id}/analysis
```
**响应示例**:
```json
{
  "scenes": [
    {
      "id": "S1",
      "summary": "客厅争吵戏",
      "location": "INT-LIVINGROOM",
      "time": "DAY",
      "characters": ["张三", "李四"],
      "props": ["茶杯", "沙发"]
    }
  ],
  "breakdown": {
    "costumes": [
      {
        "name": "商务西装",
        "character": "张三",
        "scenes": ["S1", "S3"]
      }
    ]
  }
}
```

## 2. AI生成模块
### 2.1 触发AI处理
```http
POST /scripts/{script_id}/generate
```
**请求体**:
```json
{
  "output_type": "storyboard|breakdown|schedule|all",
  "options": {
    "detail_level": "high|medium|low"
  }
}
```

### 2.2 获取生成状态（SSE）
```http
GET /scripts/{script_id}/generation/stream
```
**Headers**:
```
Accept: text/event-stream
```
**事件流示例**:
```
event: progress
data: {"stage": "costume_analysis", "progress": 45}

event: result
data: {"type": "breakdown", "url": "/downloads/breakdown.xlsx"}
```

## 3. 项目管理
### 3.1 创建项目
```http
POST /projects
```
**请求体**:
```json
{
  "name": "我的电影项目",
  "start_date": "2024-10-01",
  "team_members": [
    {"email": "director@example.com", "role": "director"}
  ]
}
```

## 4. 排期管理
### 4.1 获取智能排期
```http
GET /scripts/{script_id}/schedule
```
**查询参数**:
- `optimize_for`: `time|cost|availability` (默认: time)

**响应示例**:
```json
{
  "shooting_days": 12,
  "schedule": [
    {
      "date": "2024-10-03",
      "scenes": ["S1", "S2"],
      "location": "Studio A",
      "cast_required": ["张三", "李四"]
    }
  ]
}
```

## 5. 协作系统
### 5.1 添加评论
```http
POST /scripts/{script_id}/comments
```
**请求体**:
```json
{
  "target_element": "scene:S1",
  "content": "这个场景需要额外准备血浆道具",
  "mentions": ["user2@example.com"]
}
```

## 错误处理
**通用错误格式**:
```json
{
  "error": {
    "code": "invalid_script_format",
    "message": "不支持的文件格式",
    "details": {
      "supported_formats": [".txt", ".pdf", ".fdx"]
    }
  }
}
```

## 实时通信
**WebSocket 端点**: `/ws`  
**事件类型**:
- `script_updated`: 剧本被修改
- `comment_added`: 新增评论
- `schedule_changed`: 排期变更

## 接口沙箱
我们提供Postman集合用于测试：
```json
{
  "info": {
    "_postman_id": "12345",
    "name": "Film Production API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Upload Script",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": "/path/to/script.fdx"
            }
          ]
        },
        "url": {
          "raw": "{{base_url}}/scripts",
          "host": ["{{base_url}}"],
          "path": ["scripts"]
        }
      }
    }
  ]
}
```

## 前端对接建议
1. 使用axios拦截器处理JWT刷新
2. AI生成进度建议采用EventSource API
3. 排期冲突检测使用WebSocket实时更新
4. 大文件上传实现分片上传（>50MB时）

## Python调用示例
```python
import requests

def upload_script(file_path, project_id=None):
    url = "https://api.example.com/api/v1/scripts"
    files = {'file': open(file_path, 'rb')}
    data = {'project_id': project_id} if project_id else None
    
    response = requests.post(url, files=files, data=data)
    return response.json()

# 调用示例
result = upload_script("script.fdx", "proj_123")
print(result["id"])  # 输出: script_123
```

## 版本历史
| 版本 | 日期       | 变更说明               |
|------|------------|------------------------|
| v1.0 | 2024-06-01 | 初始版本               |
| v1.1 | 2024-06-15 | 新增SSE进度通知        |
```

---

### 关键设计说明

1. **大文件处理**：
   - 前端需实现分片上传（推荐使用`tus`协议）
   - 后端提供预签名URL直传OSS（如AWS S3）

2. **AI异步处理**：
   ```mermaid
   sequenceDiagram
       前端->>后端: 触发生成请求
       后端->>OpenAI: 发送结构化剧本
       OpenAI-->>后端: 返回处理ID
       后端->>前端: 202 Accepted
       前端->>后端: 建立SSE连接
       后端->>前端: 持续推送进度
   ```

3. **安全设计**：
   - 剧本文件扫描（病毒/恶意内容）
   - 敏感操作二次验证（如删除剧本）
   - 基于元素的细粒度权限控制

4. **性能优化**：
   - 剧本解析结果缓存（TTL 24h）
   - 排期计算使用Celery分布式任务
   - 高频查询端点添加ETag

建议先实现以下核心端点：
1. `POST /scripts` + `GET /scripts/{id}/analysis`
2. `POST /generate` + SSE进度流
3. `GET /schedule` 排期获取
