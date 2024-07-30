
def route(path, methods=['GET']):
    def decorator(handler):
        handler._route_path = path
        handler._route_methods = methods
        return handler
    return decorator

def middleware(type: str="http"):
    def decorator(handler):
        handler._middleware = type
        return handler
    return decorator

def get(path):
    return route(path, methods=['GET'])

def post(path):
    return route(path, methods=['POST'])

def ws(path):
    return route(path, methods=['WS'])
