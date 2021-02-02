# -*- coding:utf8 -*-
'''
User Form.
'''
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError
from ..models import User, Role

class EditProfileForm(Form):
    name = StringField('真实姓名', validators=[Required(), Length(1, 64, '长度必须为1-64。')])
    location = StringField('居住地', validators=[Required(), Length(1, 64, '长度必须为1-64。')])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

class EditProfileAdminForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64, '长度必须为1-64。'), Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64, '长度必须为1-64。'), Regexp('^[A-Z][A-Za-z0-9_.]*$', 0,
                                          '用户名第一个字母必须大写，且只能由字母，'
                                          '数字，下划线，点组成。')])
    password = StringField('密码', validators=[
        Required(), Length(1, 16, '长度必须为1-16。'), Regexp('^[A-Za-z0-9_.]*$', 0,
                                          '密码第只能由字母，数字，下划线，点组成。')])
    name = StringField('真实姓名', validators=[Length(0, 64, '长度必须为1-64。')])
    confirmed = BooleanField('是否验证')
    location = StringField('居住地', validators=[Length(0, 64, '长度必须为1-64。')])
    about_me = TextAreaField('关于我')
    # 选择角色
    role = SelectField('角色', coerce=int)
    submit = SubmitField('修改')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, filed):
        if self.user.email == filed.data:
            return
        else:
            raise ValidationError('暂时不支持修改邮箱地址！')

    def validate_username(self, filed):
        # 允许管理员修改 用户名，但是不能修改邮箱
        if self.user.username == filed.data:
            return
        if User.query.filter_by(username=filed.data).first():
            raise ValidationError('改用户名已被占用。')