# -*- coding:utf8 -*-
'''
index page.
'''
__all__ = []
__version__ = '0.0.1'
__author__ = 'GalaIO'

from flask import Blueprint
import app
from ..models import Remark_Attitude

# 通过实例化一个 Blueprint 类对象可以创建蓝本。
comment = Blueprint('comment', __name__)
# 动态加载到app的路由链表中
app.fetchRoute(comment, '/comment')


# 把简评模型条件填充到模板中
@comment.app_context_processor
def inject_permission():
    return dict(Remark_Attitude=Remark_Attitude)



from . import views