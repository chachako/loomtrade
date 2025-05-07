from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # 使用字典来存储每个用户的活跃连接列表
        # key: user_id (int), value: List[WebSocket]
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"User {user_id} connected. Total connections for user: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                print(f"User {user_id} disconnected a websocket. Remaining: {len(self.active_connections[user_id])}")
                if not self.active_connections[user_id]: # 如果用户没有其他连接了
                    del self.active_connections[user_id]
                    print(f"User {user_id} has no more active connections. Removed user entry.")
            else:
                print(f"Warning: Websocket not found for user {user_id} during disconnect.")
        else:
            print(f"Warning: User {user_id} not found in active connections during disconnect.")


    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"Error sending message to user {user_id} on a connection: {e}")
                    # Optionally, handle dead connections here by removing them
                    # self.disconnect(connection, user_id) # Be careful with modifying list during iteration

    async def broadcast(self, message: str):
        for user_id in list(self.active_connections.keys()): # Iterate over a copy of keys
            for connection in list(self.active_connections.get(user_id, [])): # Iterate over a copy of connections
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"Error broadcasting message to user {user_id} on a connection: {e}")
                    # Optionally, handle dead connections
                    # self.disconnect(connection, user_id)

# 全局 WebSocket 管理器实例
manager = ConnectionManager()