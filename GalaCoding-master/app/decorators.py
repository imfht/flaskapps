 # -*- coding:utf8 -*-
'''
Some useful decorator
'''

from functools import wraps
from flask import abort, redirect, url_for, render_template
from flask.ext.login import current_user
from models import Permission

# 检验权限，线检查权限，才能访问f行为
def permission_required(permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permissions):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# 检查你是否是超级管理员
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)