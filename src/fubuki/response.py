import json
from typing import List, Tuple, Union

try:
    import orjson
    use_orjson = True
except ImportError:
    use_orjson = False

class Response:
    def __init__(
        self, 
        content: str,
        content_type: str | bytes = "text/plain",
        headers: List[Tuple[Union[str, bytes], Union[str, bytes]]] = [],
        status: int = 200, 
    ) -> None:
        self.content = content.encode("utf-8") if isinstance(content, str) else content
        if isinstance(content_type, str):
            self.content_type = content_type.encode("utf-8")
        else:
            self.content_type = content_type
        self.headers = self._validate_and_encode_headers(headers)
        self.status = status
        
    def _validate_and_encode_headers(self, headers: List[Tuple[Union[str, bytes], Union[str, bytes]]]) -> List[Tuple[bytes, bytes]]:
        encoded_headers = []
        has_content_type = False
        for header in headers:
            if not isinstance(header, tuple) or len(header) != 2:
                raise TypeError("Headers must be a list of tuples (Union[str, bytes], Union[str, bytes])")
            name, value = header
            if isinstance(name, str):
                name = name.encode('latin-1')
            if isinstance(value, str):
                value = value.encode('latin-1')
            if name.lower() == b'content-type':
                has_content_type = True
            encoded_headers.append((name, value))
        if not has_content_type:
            encoded_headers.append((b'content-type', self.content_type))
        return encoded_headers
    
    async def send(self, send):
        await send({
            'type': 'http.response.start',
            'status': self.status,
            'headers': self.headers,
        })
        await send({
            'type': 'http.response.body',
            'body': self.content,
        })

class JSONResponse(Response):
    def __init__(self, content: Union[dict, list], content_type: str | bytes = "application/json", headers: List[Tuple[str | bytes]] = [], status: int = 200) -> None:
        if use_orjson:
            content = orjson.dumps(content)
        else:
            content = json.dumps(content).encode("utf-8")
        super().__init__(content, content_type, headers, status)