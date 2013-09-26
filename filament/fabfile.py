#!/usr/bin/env python2.7
import os, ConfigParser
from uuid import uuid4
from itertools import chain

from fabric import api
from fabric.api import env

from providers import Provider
from configuration import config, render
import flaskapp as flask


env.flask_dir = os.environ['FLASKPATH']
env.provider = os.path.join(env.flask_dir, 'filament', 'provider.ini')
env.build_path = '/tmp/filament/'
env.user = 'root'

SRV_ROOT = '/srv'

@api.task
def debug(module_name=None):
    app = flask.discover(module_name)
    app.run(
        host = app.config.get('HOST', '0.0.0.0'),
        port = app.config.get('PORT', 5000),
        debug = app.config.get('DEBUG', True),
        threaded = True
    )


@api.task
def map(module_name=None):
    app = flask.discover(module_name)
    print(app.url_map)
    print(app.static_folder)


@api.task
def deploy(module_name=None, resume=False, lock_root=False):
    app = flask.discover(module_name)
    lpath = os.path.realpath(os.path.join(env.flask_dir, app.name))

    # create new server
    server = Provider.load(env.provider)
    server.name = "-".join((app.name, uuid4().hex))
    server.create().wait()

    # prepare system software
    api.run('apt-get install -y openssh-server')

    # set up firewall
    api.run('mkdir /etc/iptables')
    api.put(config('iptables'), '/etc/iptables/rules')
    api.put(config('iptables.sh'), '/etc/network/if-pre-up.d/iptables')
    api.run('chmod +x /etc/network/if-pre-up.d/iptables')

    # install software
    with open(config('packages.txt')) as requirements:
        for requirement in requirements:
            print("installing requirement `{0}`...".format(requirement))
            api.run('apt-get install -y {0}'.format(requirement.strip()))

    # install python packages
    api.put(config('requirements.txt'), 'requirements.txt')
    api.run('pip3 install -r requirements.txt')
    api.run('rm requirements.txt')

    # deploy application
    rpath = os.path.join(SRV_ROOT, app.name)
    api.put(lpath, SRV_ROOT, use_sudo=True)
    api.run('chown -R www-data {0}'.format(rpath))
    api.run('chmod -R 500 {0}'.format(rpath))

    # extract socket_name
    with open(config('uwsgi.ini')) as ini:
        conf = ConfigParser.RawConfigParser()
        conf.readfp(ini)
        socket_name = conf.get('uwsgi', 'module')

    # configure web server
    render('nginx.conf', '/etc/nginx/nginx.conf',
        socket_name = socket_name,
        static_directories = [
            ( x.static_url_path, os.path.join(
                rpath,
                os.path.realpath(x.static_folder).split(lpath)[1][1:]
            )) for x in chain([app], app.blueprints.values())
               if x.static_url_path ]
    )

    # configure supervisord
    api.run('pip install supervisor')
    render('supervisord.conf', '/etc/supervisord.conf',
        flask_dir = module_name,
        location = rpath,
        ini_file = os.path.join(rpath, 'uwsgi.ini'),
    )

    # start web service
    api.run('/usr/local/bin/supervisord')
    api.run('service nginx start')

    if lock_root:
        # prepare admin user
        api.run('addgroup admin')
        api.run('adduser admin --quiet --ingroup admin --gecos ""')
        api.run('sudo -u admin mkdir /home/admin/.ssh')
        api.put('~/.ssh/id_rsa.pub', '/home/admin/.ssh/authorized_keys')
        api.run('chown admin:admin /home/admin/.ssh/authorized_keys')

        # lock down SSH
        api.put('build/sshd_config', '/etc/ssh/sshd_config')
        api.run('service ssh restart')











