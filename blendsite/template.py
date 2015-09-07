from jinja2 import Environment, FileSystemLoader
from aiohttp import web

def render_to_string(template_name, context={}):
    env = Environment(loader=FileSystemLoader())
    template = env.get_template(template_name)
    return template.render(**context)

def render_to_response(template_name, context={}):
    data = render_to_string(template_name, context)
    return web.Response(text=data)
