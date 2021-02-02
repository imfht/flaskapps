# -*- coding:utf8 -*-
'''
index route.
'''
from flask import render_template, redirect, url_for, abort, flash, request, current_app
from . import comment
from ..models import User, Role, Post, Permission, Comment
from flask.ext.login import login_required, current_user
from .forms import CommentForm
from .. import db
from .. import messages
from ..decorators import admin_required, permission_required

'''
# 赞同某评论
@comment.route('/agree/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def agree(id):

'''
# 删除某评论
# 文章所属人、评论人和管理员都可以删除评论
@comment.route('/delete/<int:id>')
@login_required
def delete(id):
    comment = Comment.query.get_or_404(id)
    access = current_user == comment.post.author or current_user == comment.author or current_user.can(Permission.MODERATE_ARTICLES)
    post_id = request.args.get('post_id')
    if access == False and comment.post_id != post_id:
        abort(404)
    # 通过过滤条件
    db.session.delete(comment)
    return redirect(url_for('main.post', id=post_id))

@comment.route('/remark/<int:id>')
@login_required
def remark(id):
    comment = Comment.query.get_or_404(id)
    post_id = int(request.args.get('post_id'))
    attitude = int(request.args.get('attitude'))
    if comment.post_id != post_id:
        abort(404)
    # 通过过滤条件
    if False == comment.remark_it(attitude, current_user.id):
        flash(messages.comment_remark_again_err)
    return redirect(url_for('main.post', id=post_id))

