import json

class JSONDecodeError(Exception):
    pass

class JSONEncodeError(Exception):
    pass

try:
    import orjson
    
    class ORJSONEncoder:
        def loads(obj) -> dict:
            try:
                return orjson.loads(obj)
            except orjson.JSONDecodeError as e:
                raise JSONDecodeError(e)

        def dumps(obj: dict) -> bytes:
            try:
                return orjson.dumps(obj)
            except orjson.JSONEncodeError as e:
                raise JSONEncodeError(e)
except ModuleNotFoundError:
    pass



class JSONEncoder:
    def loads(obj) -> dict:
        try:
            return json.loads(obj)
        except json.JSONDecodeError as e:
            raise JSONDecodeError(e)
    
    def dumps(obj: dict) -> bytes:
        try:
            return json.dumps(obj).encode("utf-8")
        except Exception as e:
            raise JSONEncodeError(e)