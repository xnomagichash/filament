import os, re, ConfigParser

from pkg_resources import resource_filename, Requirement
from fabric import api
from fabric.api import env
from jinja2 import Template



req = Requirement.parse("filament")

def config(name, require=False):
    p   = os.path.join(env.flask_dir, 'filament')
    p2  = os.path.join(p, env.flask_app.name)
    cd  = p2 if os.path.exists(p2) else p
    return os.path.join(cd, name) \
        if os.path.exists(os.path.join(cd, name)) \
      else resource_filename(req, "filament/defaults/"+name)


def render(path, dest, use_sudo=True, **kwargs):
    template = config(path)
    rendered = os.path.join(env.build_path, path)
    if not os.path.exists(env.build_path):
        os.mkdir(env.build_path)

    if os.path.exists(rendered):
        os.remove(rendered)

    with open(template) as f:
        while True:
            line = f.readline()
            if line.strip(): break
        tpl = Template(f.read())

    with open(rendered, 'w+') as f:
        f.write(tpl.render(**kwargs))
        f.flush()

    api.put(rendered, dest, use_sudo=use_sudo)

