import json as pyjson
from typing import Callable, Dict, Any

from .exceptions import ConnectionClosed
from .models.websocket import WSMessage
from .models.connection import Client, Server
from .models.asgi import ASGI
from .encorder import ORJSONEncoder, JSONEncoder, JSONDecodeError, JSONEncodeError

async def json(text: str) -> dict:
    return pyjson.loads(text)

class WebSocket:
    def __init__(self, scope: Dict[str, Any], receive: Callable, send: Callable, encorder: ORJSONEncoder | JSONEncoder):
        self.scope = scope
        self.receive = receive
        self.send = send
        self.encorder = encorder

    async def accept(self):
        await self.send({
            "type": "websocket.accept"
        })

    async def close(self, code: int = 1000):
        await self.send({
            "type": "websocket.close",
            "code": code
        })
        
    async def send_str(self, data: str):
        await self.send({
            "type": "websocket.send",
            "text": data
        })
        
    async def send_json(self, data: dict):
        await self.send({
            "type": "websocket.send",
            "text": self.encorder.dumps(data, ensure_ascii=False)
        })
        
    async def recv(self) -> WSMessage | None:
        message = await self.receive()
        if message["type"] == "websocket.disconnect":
            raise ConnectionClosed
        elif message["type"] == "websocket.connect":
            return None
        elif message["type"] == "websocket.receive":
            try:
                text = self.encorder.loads(message["text"])
            except JSONDecodeError:
                text = None
            if message["type"] == "websocket.receive":
                return WSMessage(
                    text=message["text"], 
                    json=text
                )
        else:
            raise RuntimeError("Unexpected message type: " + message["type"])