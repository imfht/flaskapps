# -*- coding:utf8 -*-
'''
Login Form.
'''
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64, '长度必须为1-64。'), Email()])
    password = PasswordField('密码', validators=[Required(), Length(1, 16, '长度必须为1-16。')])
    remember_me = BooleanField('保持登录状态')
    submit = SubmitField('登录')

class RegistrationForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64, '长度必须为1-64。'), Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64, '长度必须为1-64。'), Regexp('^[A-Z][A-Za-z0-9_.]*$', 0,
                                          '用户名第一个字母必须大写，且只能由字母，'
                                          '数字，下划线，点组成。')])
    password = PasswordField('密码', validators=[
        Required(), Length(1, 16, '长度必须为1-16。'), Regexp('^[A-Za-z0-9_.]*$', 0,
                                          '密码第只能由字母，数字，下划线，点组成。')])
    password_verify = PasswordField('确认密码', validators=[
        Required(), Length(1, 16, '长度必须为1-16。'), EqualTo('password', '必须和密码一致。')])
    submit = SubmitField('注册')

    def validate_email(self, filed):
        if User.query.filter_by(email=filed.data).first():
            raise ValidationError('该邮箱已被注册。')

    def validate_username(self, filed):
        if User.query.filter_by(username=filed.data).first():
            raise ValidationError('改用户名已被占用。')

class ResetPassword(Form):
    password = PasswordField('原密码', validators=[Required(), Length(1, 16, '长度必须为1-16。')])
    new_password = PasswordField('新密码', validators=[
        Required(), Length(1, 16, '长度必须为1-16。'), Regexp('^[A-Za-z0-9_.]*$', 0,
                                          '密码第只能由字母，数字，下划线，点组成。')])
    submit = SubmitField('提交')

class ForgetPassword(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64, '长度必须为1-64。'), Email()])
    submit = SubmitField('提交')

class ResetPasswordByConfirm(Form):
    new_password = PasswordField('新密码', validators=[
        Required(), Length(1, 16, '长度必须为1-16。'), Regexp('^[A-Za-z0-9_.]*$', 0,
                                          '密码第只能由字母，数字，下划线，点组成。')])
    submit = SubmitField('提交')
