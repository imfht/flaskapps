# -*- coding:utf8 -*-
'''
index page.
'''
__all__ = []
__version__ = '0.0.1'
__author__ = 'GalaIO'

from flask import Blueprint
import app
from ..models import Permission

# 通过实例化一个 Blueprint 类对象可以创建蓝本。
auth = Blueprint('auth', __name__)
# 动态加载到app的路由链表中
app.fetchRoute(auth, '/auth')

# 把权限条件填充到模板中
@auth.app_context_processor
def inject_permission():
    return dict(Permission=Permission)


from . import views