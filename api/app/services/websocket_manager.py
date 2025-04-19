from typing import Dict, Set, Any
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # 所有活跃连接
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "projects": set(),  # 项目相关通知
            "scripts": set(),   # 剧本相关通知
            "analysis": set(),  # AI分析相关通知
        }
        
        # 用户订阅的特定资源
        self.user_subscriptions: Dict[WebSocket, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        """建立WebSocket连接"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        self.user_subscriptions[websocket] = {channel}
    
    async def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        # 从所有频道中移除连接
        for channel in self.user_subscriptions.get(websocket, set()):
            self.active_connections[channel].remove(websocket)
        
        # 清理订阅信息
        if websocket in self.user_subscriptions:
            del self.user_subscriptions[websocket]
    
    async def subscribe(self, websocket: WebSocket, channel: str):
        """订阅特定频道"""
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        if websocket not in self.user_subscriptions:
            self.user_subscriptions[websocket] = set()
        self.user_subscriptions[websocket].add(channel)
    
    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """取消订阅特定频道"""
        if channel in self.active_connections:
            self.active_connections[channel].remove(websocket)
        if websocket in self.user_subscriptions:
            self.user_subscriptions[websocket].remove(channel)
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """向特定频道广播消息"""
        if channel not in self.active_connections:
            return
        
        # 添加时间戳
        message["timestamp"] = datetime.utcnow().isoformat()
        
        # 转换为JSON字符串
        message_str = json.dumps(message, ensure_ascii=False)
        
        # 广播消息
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(message_str)
            except:
                # 如果发送失败，将在下一次清理连接
                pass
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """发送个人消息"""
        message["timestamp"] = datetime.utcnow().isoformat()
        await websocket.send_text(json.dumps(message, ensure_ascii=False))

# 创建全局连接管理器实例
manager = ConnectionManager()

# 通知类型定义
class NotificationType:
    SCRIPT_UPLOAD = "script_upload"
    SCRIPT_PARSE = "script_parse"
    SCRIPT_ANALYSIS = "script_analysis"
    PROJECT_UPDATE = "project_update"
    RESOURCE_UPDATE = "resource_update"
    ERROR = "error"

async def notify_script_upload(script_id: int, status: str, message: str):
    """通知剧本上传状态"""
    await manager.broadcast_to_channel("scripts", {
        "type": NotificationType.SCRIPT_UPLOAD,
        "script_id": script_id,
        "status": status,
        "message": message
    })

async def notify_script_parse(script_id: int, status: str, progress: float, message: str):
    """通知剧本解析进度"""
    await manager.broadcast_to_channel("scripts", {
        "type": NotificationType.SCRIPT_PARSE,
        "script_id": script_id,
        "status": status,
        "progress": progress,
        "message": message
    })

async def notify_script_analysis(script_id: int, status: str, progress: float, message: str):
    """通知AI分析进度"""
    await manager.broadcast_to_channel("analysis", {
        "type": NotificationType.SCRIPT_ANALYSIS,
        "script_id": script_id,
        "status": status,
        "progress": progress,
        "message": message
    })

async def notify_project_update(project_id: int, update_type: str, message: str):
    """通知项目更新"""
    await manager.broadcast_to_channel(f"project_{project_id}", {
        "type": NotificationType.PROJECT_UPDATE,
        "project_id": project_id,
        "update_type": update_type,
        "message": message
    })

async def notify_error(error_type: str, message: str, details: Dict[str, Any] = None):
    """通知错误信息"""
    await manager.broadcast_to_channel("errors", {
        "type": NotificationType.ERROR,
        "error_type": error_type,
        "message": message,
        "details": details
    }) 