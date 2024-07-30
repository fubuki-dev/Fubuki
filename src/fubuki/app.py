import re
from typing import Callable, get_type_hints
import inspect

from . import encorder
from .request import Request
from .response import Response
from .websocket import WebSocket

class Fubuki:
    def __init__(self, use_orjson: bool = True):
        self.__static_routes = []
        self.__dynamic_routes = []
        self.__raw_middleware = []
        self.__middleware = {
            "http": [],
            "websocket": []
        }
        if use_orjson:
            if hasattr(encorder, "ORJSONEncoder"):
                self.encorder = encorder.ORJSONEncoder
            else:
                self.encorder = encorder.JSONEncoder
        else:
            self.encorder = encorder.JSONEncoder

    async def handle_middleware(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive, send)
            for func in self.__middleware["http"]:
                await func(request)

    def add_middleware(self, middleware: Callable):
        self.__raw_middleware.append(middleware)

    def add_route(self, controller_class):
        for attr in dir(controller_class):
            method = getattr(controller_class, attr)
            if hasattr(method, "_route_path"):
                route_pattern = re.compile(method._route_path)
                route = {
                    "path": route_pattern,
                    "func": method,
                    "methods": method._route_methods
                }
                if self._is_static_route(method._route_path):
                    self.__static_routes.append(route)
                else:
                    self.__dynamic_routes.append(route)
            elif hasattr(method, "_middleware"):
                if self.__middleware.get(method._middleware) is None:
                    self.__middleware[method._middleware] = []

    def _is_static_route(self, path):
        return not re.search(r'[\(\)\?\*]', path)

    async def __call__(self, scope, receive, send):
        await self.handle_middleware(scope, receive, send)
        for func in self.__raw_middleware:
            await func(scope, receive, send)
        if scope['type'] == 'http':
            path = scope['path']
            method = scope['method']
            handler = self.find_handler(path, method)
            if handler:
                path_params = handler['match'].groupdict()
                func = handler["func"]
                sig = inspect.signature(func)
                type_hints = get_type_hints(func)

                func_kwargs = path_params.copy()
                if Request in type_hints.values():
                    request = Request(scope, receive, send)
                    for name, hint in type_hints.items():
                        if hint is Request:
                            func_kwargs[name] = request

                response = await func(**func_kwargs)
                
                if isinstance(response, Response):
                    await response.send(send)
            else:
                await send({
                    'type': 'http.response.start',
                    'status': 404,
                    'headers': [(b'content-type', b'text/plain')],
                })
                await send({
                    'type': 'http.response.body',
                    'body': b'Not found',
                })
        elif scope['type'] == 'websocket':
            path = scope['path']
            method = "WS"
            for route in self.__dynamic_routes:
                if route["path"].match(path) and method in route["methods"]:
                    handler = route["func"]
                    break
            else:
                handler = self.not_found
            websocket = WebSocket(scope, receive, send)
            await handler(websocket)

    def find_handler(self, path, method):
        for route in self.__static_routes:
            if route["path"].pattern == path and method in route["methods"]:
                return {"func": route["func"], "match": re.match(route["path"], path)}
        for route in self.__dynamic_routes:
            match = route["path"].fullmatch(path)
            if match and method in route["methods"]:
                return {"func": route["func"], "match": match}
        return None

    async def not_found(self, scope, receive, send):
        return {"status": 404, "body": {"message": "Not Found"}}

    def run(self, host="0.0.0.0", port=8000):
        import uvicorn
        uvicorn.run(self, host=host, port=port)