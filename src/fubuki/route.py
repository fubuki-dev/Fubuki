def route(path, methods=['GET'], schema=True):
    def decorator(handler):
        handler._route_path = path
        handler._route_methods = methods
        handler._include_in_schema = schema
        return handler
    return decorator

def middleware(type: str="http"):
    def decorator(handler):
        handler._middleware = type
        return handler
    return decorator

def get(path, schema=True):
    return route(path, methods=['GET'], schema=schema)

def post(path, schema=True):
    return route(path, methods=['POST'], schema=schema)

def ws(path, schema=True):
    return route(path, methods=['WS'], schema=schema)