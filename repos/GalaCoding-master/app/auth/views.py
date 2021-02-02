# -*- coding:utf8 -*-
'''
index route.
'''
from flask import request, render_template, redirect, url_for, flash
from . import auth
from forms import LoginForm, RegistrationForm, ResetPassword, ForgetPassword, ResetPasswordByConfirm
from ..models import User, Role
from flask.ext.login import login_user, login_required, logout_user, current_user
from .. import messages
from .. import  db
from ..email import send_email

# 定义路由函数
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # 每次登陆更新时间
            user.ping()
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(messages.wrong_username_password)
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(messages.log_out)
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                            username = form.username.data,
                            password = form.password.data,
                            role=Role.query.filter_by(name='User').first())
        # 新注册需要更新用户的 头像链接
        user.generate_avatar_url()
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Please, Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash(messages.send_register_confirm)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(messages.confirm_ok)
        db.session.add(current_user)
    else:
        flash(messages.confirm_invalid)
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user is not None and current_user.is_authenticated:
        if not current_user.confirmed\
            and request.endpoint[:5] != 'auth.'\
            and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return  redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html'), 200

@auth.route('/resend_confirm')
@login_required
def resend_confirm():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash(messages.confirm_resend)
    return redirect(url_for('main.index'))

@auth.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = ResetPassword()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash(messages.reset_password_ok)
            return redirect(url_for('main.index'))
        flash(messages.reset_password_err)
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset_password_confirm/<token>', methods=['GET', 'POST'])
def reset_password_confirm(token):
    '''token = request.args.get('token')
    if token is None:
        flash(messages.confirm_invalid)
        return redirect('main.index')'''
    user_id = User.parse_confirm_token(token)
    if user_id is None:
        flash(messages.confirm_invalid)
        return redirect('main.index')
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash(messages.user_not_found)
        return redirect('main.index')
    form = ResetPasswordByConfirm()
    if form.validate_on_submit():
        user.password = form.new_password.data
        db.session.add(user)
        flash(messages.reset_password_ok)
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_confirmation_token()
            send_email(user.email, 'Reset you password', 'auth/email/forget_password', user=user, token=token)
            flash(messages.send_register_confirm)
            return redirect(url_for('auth.login'))
        flash(messages.user_not_found)
    return render_template('auth/forget_password.html', form=form)