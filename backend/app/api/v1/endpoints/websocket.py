from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
# 假设的依赖项，用于从 token 获取 user_id
# from app.api.deps import get_current_user # 取消注释并实现此依赖项以进行实际认证
# from app.models.user import User # 如果 get_current_user 返回 User 模型

from app.services.websocket_manager import manager # 导入全局管理器实例

router = APIRouter()

# 注意：实际应用中，user_id 通常不应直接从路径参数获取，
# 而是通过认证机制（例如，从 JWT token 中提取）来安全地确定。
# 此处为了简化示例，直接使用路径参数。
# 在生产环境中，强烈建议实现基于 Token 的认证。

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket 连接端点。

    认证:
    - TODO: 实现认证逻辑。
      例如，可以在连接握手阶段验证 Authorization header 中的 Bearer token，
      或者要求客户端在连接后发送一个认证消息。
      如果认证失败，应调用 `await websocket.close(code=status.WS_1008_POLICY_VIOLATION)`。

    Args:
        websocket (WebSocket): WebSocket 连接对象。
        user_id (int): 从路径参数获取的用户 ID。
                       在生产中，这应该从认证的 token 中获取。
    """
    # 此处应添加认证逻辑
    # 例如:
    # try:
    #     # current_user: User = await get_current_user_ws(websocket) # 一个假设的函数，用于在 ws 握手时验证 token
    #     # user_id = current_user.id
    #     pass # 假设认证成功
    # except HTTPException:
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #     return

    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # (占位符) 处理接收到的消息
            print(f"User {user_id} sent: {data}")
            # 例如，简单回显
            await websocket.send_text(f"Message text was: {data}, from user {user_id}")
            # 或者广播给所有用户 (如果适用)
            # await manager.broadcast(f"User {user_id} says: {data}")
            # 或者只发送给特定用户
            # await manager.send_personal_message(f"You said: {data}", user_id)
    except WebSocketDisconnect:
        print(f"WebSocketDisconnect for user {user_id}")
    except Exception as e:
        print(f"Exception for user {user_id}: {e}")
    finally:
        manager.disconnect(websocket, user_id)
        print(f"Connection closed for user {user_id}")

# 如果需要更安全的 user_id 获取，可以考虑类似这样的依赖项（需要实现）:
# async def get_current_user_ws(websocket: WebSocket):
#     # 从 websocket.headers 或初始消息中获取 token
#     # token = websocket.query_params.get("token") or websocket.headers.get("Authorization")
#     # if not token:
#     #     raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
#     # user = await get_current_user(token.split("Bearer ")[1] if token.startswith("Bearer ") else token) # 使用现有的 get_current_user
#     # if not user:
#     #     raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
#     # return user
#
# @router.websocket("/ws") # 无需 user_id 在路径中
# async def secure_websocket_endpoint(websocket: WebSocket, current_user: User = Depends(get_current_user_ws_dependency_placeholder)):
#     user_id = current_user.id
#     await manager.connect(websocket, user_id)
#     # ... rest of the logic