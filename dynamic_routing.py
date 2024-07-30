import re
import time

try:
    import regex as re
    print("regex library detected and imported.")
except ModuleNotFoundError:
    pass

from asgiref.compatibility import guarantee_single_callable

class ASGIApp:
    def __init__(self):
        self.routes = []

    def route(self, path):
        pattern = re.compile(path)
        def wrapper(handler):
            self.routes.append((pattern, handler))
            return handler
        return wrapper

    async def __call__(self, scope, receive, send):
        start = time.time()
        assert scope['type'] == 'http'
        path = scope['path']
        for pattern, handler in self.routes:
            match = pattern.fullmatch(path)
            if match:
                scope['path_params'] = match.groupdict()
                await handler(scope, receive, send)
                response_time = time.time() - start
                return
        await self.default_response(scope, receive, send)
        response_time = time.time() - start
        print(f"Request to {path} took {response_time:.6f} seconds")

    async def default_response(self, scope, receive, send):
        response = {
            'type': 'http.response.start',
            'status': 404,
            'headers': [(b'content-type', b'text/plain')],
        }
        await send(response)
        await send({
            'type': 'http.response.body',
            'body': b'Not found',
        })

app = ASGIApp()

@app.route(r'/')
async def homepage(scope, receive, send):
    response = {
        'type': 'http.response.start',
        'status': 200,
        'headers': [(b'content-type', b'text/plain')],
    }
    await send(response)
    await send({
        'type': 'http.response.body',
        'body': b'Hello, World!',
    })

@app.route(r'/hello')
async def hello(scope, receive, send):
    response = {
        'type': 'http.response.start',
        'status': 200,
        'headers': [(b'content-type', b'text/plain')],
    }
    await send(response)
    await send({
        'type': 'http.response.body',
        'body': b'Hello!',
    })

@app.route(r'/user/(?P<user_id>\d+)')
async def user_profile(scope, receive, send):
    user_id = scope['path_params']['user_id']
    response = {
        'type': 'http.response.start',
        'status': 200,
        'headers': [(b'content-type', b'text/plain')],
    }
    await send(response)
    await send({
        'type': 'http.response.body',
        'body': f'User ID: {user_id}'.encode(),
    })
    
@app.route(r'/article/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+)')
async def article_detail(scope, receive, send):
    year = scope['path_params']['year']
    month = scope['path_params']['month']
    slug = scope['path_params']['slug']
    response = {
        'type': 'http.response.start',
        'status': 200,
        'headers': [(b'content-type', b'text/plain')],
    }
    await send(response)
    await send({
        'type': 'http.response.body',
        'body': f'Article: {year}/{month} - {slug}'.encode(),
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
