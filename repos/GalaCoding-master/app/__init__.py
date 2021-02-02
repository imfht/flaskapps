# -*- coding:utf8 -*-
'''
The flask app, include models, templates, static file and route mapper.
'''
__all__ = []
__version__ = '0.0.1'
__author__ = 'GalaIO'

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import config, root_dir
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.moment import Moment

# 定义了数据库实例，在随后初始化，传入app上下文
db = SQLAlchemy()
# 实例化bootstrap
bootstrap = Bootstrap()
# 实例化登陆管理类
login_manager = LoginManager()
# session protection属性可以设为None basic strong，可以提高不同安全等级防止用户会话遭篡改
# 如果是 strong，flask-login会监控客户端ip和浏览器的代理信息，发现异动就登出用户
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
# 初始化邮箱类
mail = Mail()
# 初始化本地化时间类
moment = Moment()

# 蓝图表，可以动态加载进去
route_list = []
# 提供一个函数简化操作
def fetchRoute(blueprint, prefix=None):
    tmpList = [blueprint, prefix]
    route_list.append(tmpList)

# 延迟创建app， 为了让视图和模型与创建分开
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # 初始化一些flask扩展库，依赖于flask的app上下文环境
    db.init_app(app)
    # 初始化bootstrap
    bootstrap.init_app(app)
    # 初始化登陆管理
    login_manager.init_app(app)
    # 初始化邮件
    mail.init_app(app)
    # 初始化moment
    moment.init_app(app)
    # 附加路由和自定义的错误页面
    app_dir = os.path.join(root_dir, 'app')
    # 逐个执行各个路由映射脚本，添加到route_list中
    for routes in os.listdir(app_dir):
        rou_path = os.path.join(app_dir, routes)
        if (not os.path.isfile(rou_path)) and routes != 'static' and routes != 'templates':
            __import__('app.' + routes)
    # 从route_list中引入蓝图
    for blueprints in route_list:
        if blueprints[1] != None:
            app.register_blueprint(blueprints[0], url_prefix = blueprints[1])
        else:
            app.register_blueprint(blueprints[0])
    #返回app实例，让外部模块继续使用
    return app