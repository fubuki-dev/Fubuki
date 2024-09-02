import json
from typing import Any, Dict, List, Union
from urllib.parse import parse_qs

from multipart import MultipartDecoder
from pydantic import BaseModel, ValidationError
from yarl import URL
try:
    import orjson
    use_orjson = True
except ModuleNotFoundError:
    use_orjson = False

class Client:
    def __init__(self, ip: str, port: int = None, user_agent: str = None):
        self.ip = ip
        self.port = port
        self.user_agent = user_agent

    def __repr__(self):
        return f"Client(ip={self.ip}, port={self.port}, user_agent={self.user_agent})"

class Request:
    def __init__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send
        self._body = None
        self._form = None
        self._json = None
        self._url = URL(self.scope["path"])  # yarl.URL インスタンスを使って URL を解析

    @property
    def method(self):
        return self.scope["method"]

    @property
    def path(self):
        return self._url.path

    @property
    def headers(self):
        return {
            k.decode("latin1"): v.decode("latin1") for k, v in self.scope["headers"]
        }

    @property
    def query_params(self):
        parsed_query = parse_qs(self.scope["query_string"].decode("utf-8"))
        query_dict = {k: v[0] if len(v) == 1 else v for k, v in parsed_query.items()}
        return query_dict

    @property
    def url(self):
        return str(self._url)

    @property
    def client(self):
        client_info = self.scope.get("client")
        if client_info:
            ip = client_info[0]
            port = client_info[1] if len(client_info) > 1 else None
        else:
            ip = None
            port = None
        user_agent = self.headers.get("user-agent")
        return Client(ip=ip, port=port, user_agent=user_agent)

    async def body(self):
        if self._body is None:
            self._body = await self._receive_body()
        return self._body

    async def _receive_body(self):
        body = b""
        more_body = True
        while more_body:
            message = await self.receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
        return body

    async def json(self) -> Dict[str, Any]:
        if self._json is None:
            body = await self.body()
            if not use_orjson:
                self._json = json.loads(body)
            else:
                self._json = orjson.loads(body)
        return self._json

    async def form(self) -> Dict[str, Any]:
        if self._form is None:
            content_type = self.headers.get("content-type", "")
            if "multipart/form-data" in content_type:
                boundary = content_type.split("boundary=")[-1]
                decoder = MultipartDecoder(await self.body(), boundary.encode())
                self._form = {
                    part.name.decode(): part.content for part in decoder.parts
                }
            else:
                self._form = {}
        return self._form

    async def parse_body(self, model: BaseModel) -> BaseModel:
        try:
            body_data = await self.json()
            return model.model_validate(body_data)
        except ValidationError as e:
            raise e

    async def text(self) -> str:
        body = await self.body()
        return body.decode("utf-8")

    async def input(self, key: str, default: Any = None) -> Any:
        data = {**self.query_params, **await self.json(), **await self.form()}
        return data.get(key, default)

    async def has(self, key: str) -> bool:
        data = {**self.query_params, **await self.json(), **await self.form()}
        return key in data

    async def all(self) -> Dict[str, Any]:
        return {**self.query_params, **await self.json(), **await self.form()}

    async def only(self, keys: List[str]) -> Dict[str, Any]:
        data = await self.all()
        return {key: data[key] for key in keys if key in data}

    async def except_(self, keys: List[str]) -> Dict[str, Any]:
        data = await self.all()
        return {key: value for key, value in data.items() if key not in keys}
