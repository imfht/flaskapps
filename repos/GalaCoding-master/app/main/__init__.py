# -*- coding:utf8 -*-
'''
index page.
'''
__all__ = []
__version__ = '0.0.1'
__author__ = 'GalaIO'

from flask import Blueprint
import app

# 通过实例化一个 Blueprint 类对象可以创建蓝本。
main = Blueprint('main', __name__)
# 动态加载到app的路由链表中
app.fetchRoute(main)

'''
@app.fetchBlueprints(None)
def createBuleprint():
    return Blueprint('main', __name__)
'''
from . import views, errors