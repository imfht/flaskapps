# -*- coding:utf8 -*-
'''
index route.
'''
from flask import render_template, redirect, url_for, abort, flash, request, current_app
from . import user
from ..models import User, Role, Post, Permission
from flask.ext.login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from .. import messages
from ..decorators import admin_required, permission_required

# 定义路由函数
@user.route('/<username>', methods=['GET', 'POST'])
def profile(username):
    tmp_user = User.query.filter_by(username=username).first()
    if tmp_user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = tmp_user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user/user.html', user=tmp_user, posts=posts, pagination=pagination)

# 用户编辑资料页
@user.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(messages.update_profile_ok)
        return redirect(url_for('user.profile', username=current_user.username))
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    form.name.data = current_user.name
    return render_template('user/edit.html', form=form)

# 直接索引用户资料页，同时需要管理员权限
@user.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        # 不能修改邮件
        # user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(messages.update_profile_ok)
        return redirect(url_for('user.profile', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('user/edit.html', form=form, user=user)

@user.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    if current_user.username == username:
        flash(messages.follow_youself_err)
        return redirect(url_for('user.profile', username=username))
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(messages.user_not_found)
        return redirect('main.index')
    if current_user.is_following(user):
        flash(messages.follow_again_err)
        return redirect(url_for('user.profile', username=username))
    # 过滤完成，允许关注
    current_user.follow(user)
    flash(messages.follow_ok)
    return redirect(url_for('user.profile', username=username))

@user.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    if current_user.username == username:
        flash(messages.unfollow_youself_err)
        return redirect(url_for('user.profile', username=username))
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(messages.user_not_found)
        return redirect('main.index')
    if not current_user.is_following(user):
        flash(messages.unfollow_again_err)
        return redirect(url_for('user.profile', username=username))
    # 过滤完成，允许取消关注
    current_user.unfollow(user)
    flash(messages.unfollow_ok)
    return redirect(url_for('user.profile', username=username))

@user.route('/manage')
@login_required
@permission_required(Permission.MODERATE_USERS)
def manage():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.last_seen.desc()).paginate(
        page, per_page=current_app.config['USERS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('user/manage.html', users=users, pagination=pagination)


@user.route('/delete/<username>')
@login_required
@permission_required(Permission.MODERATE_USERS)
def delete(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash(messages.user_not_found)
    else:
        # 依次删除用户及其文章，否则文章会存在空用户索引
        posts = u.posts.all()
        for post in posts:
            db.session.delete(post)
        db.session.delete(u)
    return redirect(url_for('user.manage'))
