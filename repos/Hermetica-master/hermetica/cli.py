#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
main.py
hermetica main script
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-04-24'
import os
import click
from hermetica.scaffold.app import App
from hermetica.scaffold.config import Config
from hermetica.scaffold.wsgi import WSGI
from hermetica.scaffold.api import API
from hermetica.scaffold.model import Model
from hermetica.scaffold.test import Test
from hermetica.scaffold.docker import Docker
from hermetica.scaffold.extension import Extension
from hermetica.scaffold.pipfile import Pipfile
from hermetica.scaffold.decorator import Decorator

@click.group()
def main():
    pass

@main.command()
@click.option('--api', default='restful', type=click.Choice(['restful', 'decorator', 'class']), help='Flask-Restful or Flask decorator or methodview')
@click.option('--db', default=None, type=click.Choice(['sqlalchemy', 'mongoengine']), help='SQLAlchemy or Mongoengine or None')
@click.option('--decorator', default=False, is_flag=True, help='create decorator or None')
@click.option('--redis', default=False, is_flag=True, flag_value='redis', help='using Redis or None')
@click.option('--docker', default=False, is_flag=True, flag_value='docker', help='using container')
def init(api, db, decorator, redis, docker):
    """ initialize your flask app
    """
    dirs = ['./app/', './test/', './config/', './app/api/v1/', './app/models/']
    for dir in dirs:
        if os.path.exists(os.path.dirname(dir)):
            click.echo('[WARNING] directory {} is already exists, skip to create this directory'.format(dir))
            continue
        os.makedirs(os.path.dirname(dir))

    app = App(db=db, redis=redis, api=api)
    pipfile = Pipfile(db=db, redis=redis)
    wsgi = WSGI(db=db)
    config = Config(db=db, redis=redis)
    extension = Extension(db=db, redis=redis)
    test = Test(db=db, name='root')
    api = API(api=api, name='root')
    decorator = Decorator(name='root')

    with open('./Pipfile', 'w') as f:
        f.write(pipfile.create_pipfile())
    with open('wsgi.py', 'w') as f:
        f.write(wsgi.create_wsgi())

    with open('app/__init__.py', 'w') as f:
        f.write(app.create_app__init__())
    with open('app/extensions.py', 'w') as f:
        f.write(extension.create_extensions())
    if decorator:
        with open('app/decorators.py', 'w') as f:
            f.write(decorator.create_decorators())

    with open('config/__init__.py', 'w') as f:
        f.write(config.create_config(name='config', env='test'))
    with open('config/development.py', 'w') as f:
        f.write(config.create_config(name='development', env='development'))
    with open('config/production.py', 'w') as f:
        f.write(config.create_config(name='production', env='production'))

    if docker:
        docker = Docker(db=db, redis=redis)
        with open('Dockerfile', 'w') as f:
            f.write(docker.create_dockerfile())
        with open('docker-compose.yml', 'w') as f:
            f.write(docker.create_docker_compose_yml())

    with open('test/__init__.py', 'w') as f:
        f.write(test.create__init__())
    with open('nose.cfg', 'w') as f:
        f.write(test.create_nose_cfg())

    with open('app/api/__init__.py', 'w') as f:
        f.write(api.create__init__())
    with open('app/api/v1/__init__.py', 'w') as f:
        pass
    with open('app/api/v1/root.py', 'w') as f:
        f.write(api.create_api())

    if db:
        model = Model(db=db, name='root')
        with open('app/models/__init__.py', 'w') as f:
            f.write(model.create__init__())
        with open('app/models/root.py', 'w') as f:
            f.write(model.create_model())

@main.command()
@click.argument('name', type=str, required=True)
@click.option('--api', default='restful', type=click.Choice(['restful', 'decorator', 'class']), help='Flask-Restful or Flask decorator or methodview')
@click.option('--version', default='v1', help='API version')
def api(name, api, version):
    """ create api
    """
    path = 'app/api/{}/{}.py'.format(version, name)
    api = API(api=api, name=name)
    with open(path, 'w') as f:
        f.write(api.create_api())

@main.command()
@click.argument('name', type=str, required=True)
@click.option('--db', default='sqlalchemy', type=click.Choice(['sqlalchemy', 'mongoengine']), help='SQLAlchemy or Mongoengine or None')
def model(name, db):
    """ create model
    """
    path = 'app/models/{}.py'.format(name)
    model = Model(db=db, name=name)
    with open(path, 'w') as f:
        f.write(model.create_model())

@main.command()
@click.argument('name', type=str, required=True)
def decorator(name):
    """ create decorator
    """
    decorator = Decorator(name=name)
    with open('app/decorators.py', 'a') as f:
        f.write(decorator.create_decorator())
