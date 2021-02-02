# -*- coding:utf8 -*-
'''
User Form.
'''
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError
from ..models import User, Role
from flask import current_app

class CommentForm(Form):
    comment = TextAreaField('记录你的声音', validators=[Required()])
    submit = SubmitField('提交')

    def validate_comment(self, filed):
        if len(filed.data) > current_app.config['COMMENT_MAX_LEN']:
            ValidationError('评论不可超过'+ current_app.config['COMMENT_MAX_LEN'] +'个字符！！')
