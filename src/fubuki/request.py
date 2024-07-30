import json
from typing import Optional, Dict, Any

from pydantic import BaseModel, ValidationError
from yarl import URL

try:
    import orjson
    use_orjson = True
except ImportError:
    use_orjson = False

class Request:
    def __init__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send
        self._body = None
        self._url = URL(self.scope['path'])  # yarl.URL インスタンスを使って URL を解析

    @property
    def method(self):
        return self.scope['method']

    @property
    def path(self):
        return self._url.path

    @property
    def headers(self):
        return self.scope['headers']

    @property
    def query_params(self):
        return self._url.query

    @property
    def url(self):
        return str(self._url)

    async def body(self):
        if self._body is None:
            self._body = await self._receive_body()
        return self._body

    async def _receive_body(self):
        body = b''
        more_body = True
        while more_body:
            message = await self.receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)
        return body

    async def json(self) -> Dict[str, Any]:
        body = await self.body()
        if not use_orjson:
            return json.loads(body)
        else:
            return orjson.loads(body)

    async def parse_body(self, model: BaseModel) -> BaseModel:
        try:
            body_data = await self.json()
            return model.model_validate(body_data)
        except ValidationError as e:
            raise e