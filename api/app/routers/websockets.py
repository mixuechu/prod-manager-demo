from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
from ..services.websocket_manager import manager

router = APIRouter(tags=["websockets"])

@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    """
    WebSocket连接端点
    """
    await manager.connect(websocket, channel)
    try:
        while True:
            # 等待客户端消息
            data = await websocket.receive_text()
            
            # 这里可以处理客户端发送的消息
            # 例如订阅/取消订阅特定频道
            try:
                message = {
                    "message": "received",
                    "channel": channel,
                    "data": data
                }
                await manager.send_personal_message(websocket, message)
            except ValueError as e:
                error_message = {
                    "error": str(e)
                }
                await manager.send_personal_message(websocket, error_message)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

@router.websocket("/ws/project/{project_id}")
async def project_websocket_endpoint(websocket: WebSocket, project_id: int):
    """
    项目特定的WebSocket连接
    """
    channel = f"project_{project_id}"
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            message = {
                "message": "received",
                "project_id": project_id,
                "data": data
            }
            await manager.send_personal_message(websocket, message)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

@router.websocket("/ws/script/{script_id}")
async def script_websocket_endpoint(websocket: WebSocket, script_id: int):
    """
    剧本特定的WebSocket连接
    """
    channel = f"script_{script_id}"
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            message = {
                "message": "received",
                "script_id": script_id,
                "data": data
            }
            await manager.send_personal_message(websocket, message)
    except WebSocketDisconnect:
        await manager.disconnect(websocket) 