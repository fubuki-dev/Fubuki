from typing import List, Tuple, Union

from jinja2 import Environment as Jinja2Environment
from jinja2 import FileSystemLoader as Jinja2FileSystemLoader
from mako.lookup import TemplateLookup as MakoTemplateLookup

from .response import Response

class TemplateResponse(Response):
    def __init__(self, template_name, context: dict={}, status: int=200, headers: List[Tuple[Union[str, bytes], Union[str, bytes]]] = [], content_type: str | bytes = "text/html", engine: str="jinja2", tmpl_dir: str | list="templates"):
        self.engine = engine
        self.template_name = template_name
        self.context = context
        self.status = status
        if isinstance(content_type, str):
            self.content_type = content_type.encode("utf-8")
        else:
            self.content_type = content_type
        self.headers = self._validate_and_encode_headers(headers)
        if engine == 'jinja2':
            if isinstance(tmpl_dir, list):
                tmpl_dir = tmpl_dir[0]
            self.env = Jinja2Environment(loader=Jinja2FileSystemLoader(tmpl_dir))
        elif engine == 'mako':
            if isinstance(tmpl_dir, str):
                tmpl_dir = [tmpl_dir]
            self.lookup = MakoTemplateLookup(directories=tmpl_dir)
        else:
            raise ValueError(f"Unsupported template engine: {engine}")

    async def send(self, send):
        if self.engine == 'jinja2':
            template = self.env.get_template(self.template_name)
            content = template.render(self.context)
        elif self.engine == 'mako':
            template = self.lookup.get_template(self.template_name)
            content = template.render(**self.context)
        elif self.engine == 'minijinja':
            template = self.env.get_template(self.template_name)
            content = template.render(self.context)
        await send({
            'type': 'http.response.start',
            'status': self.status,
            'headers': self.headers,
        })
        await send({
            'type': 'http.response.body',
            'body': content.encode('utf-8'),
        })