import json
import functools
import hashlib
from typing import Callable, Dict, Any, Tuple, List

from .handler import CacheHandler
from ...request import Request
from ...response import JSONResponse, Response

def serialize_headers(headers: Any) -> Dict[str, str]:
    if isinstance(headers, dict):
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in headers.items()}
    elif isinstance(headers, list):
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in headers}
    else:
        raise TypeError("Unsupported headers format")

def deserialize_headers(headers: Dict[str, str]) -> List[Tuple[bytes, bytes]]:
    return [(k.encode('utf-8'), v.encode('utf-8')) for k, v in headers.items()]

def cache(cache_handler: CacheHandler, expire: int = 60):
    def decorator_cacheable(func: Callable):
        @functools.wraps(func)
        async def wrapper_cacheable(*args, **kwargs):
            request: Request = next((arg for arg in args if isinstance(arg, Request)), None)
            if request is None:
                request = kwargs.get('request', None)
            if request is None:
                raise ValueError("Request object not found in arguments")

            # Collecting all relevant parts of the request
            cache_key_parts = [func.__name__]
            cache_key_parts.append(f"method:{request.method}")
            cache_key_parts.append(f"path:{request.path}")
            cache_key_parts.append(f"headers:{json.dumps(serialize_headers(dict(request.headers)))}")
            if request.query_params:
                cache_key_parts.append(f"query_params:{str(request.query_params)}")
            if request.scope.get("path_params"):
                cache_key_parts.append(f"path_params:{json.dumps(request.scope['path_params'])}")
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                cache_key_parts.append(f"body:{body.decode('utf-8')}")

            raw_key = ":".join(cache_key_parts)
            cache_key = hashlib.sha256(raw_key.encode()).hexdigest()

            cached_response = await cache_handler.get(cache_key)
            if cached_response:
                print("Cache hit")
                if isinstance(cached_response, str):
                    cached_response = json.loads(cached_response)
                headers = deserialize_headers(cached_response.get("headers", {}))
                content = cached_response.get("content", "")
                status = cached_response.get("status", 200)
                content_type = cached_response.get("content_type", "application/json")
                return Response(content=content, headers=headers, content_type=content_type, status=status)

            response = await func(*args, **kwargs)

            if isinstance(response, JSONResponse):
                cache_data = {
                    "content": response.content.decode("utf-8"),
                    "headers": serialize_headers(dict(response.headers)),
                    "content_type": response.content_type.decode("utf-8") if isinstance(response.content_type, bytes) else response.content_type,
                    "status": response.status
                }
            elif isinstance(response, Response):
                response_content = response.content.decode("utf-8") if isinstance(response.content, bytes) else response.content
                cache_data = {
                    "content": response_content,
                    "headers": serialize_headers(dict(response.headers)),
                    "content_type": response.content_type.decode("utf-8") if isinstance(response.content_type, bytes) else response.content_type,
                    "status": response.status
                }
            else:
                raise ValueError("Unsupported response type for caching")

            await cache_handler.set(cache_key, json.dumps(cache_data), expire)

            return response

        return wrapper_cacheable
    return decorator_cacheable
