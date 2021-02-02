from . import admin
from ..models import User
from ..models import Article
from .forms import LoginForm, RegistrationForm, PostForm
from .. import db
from config import is_exist_admin
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash
from flask.ext.login import current_user
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import login_required


@admin.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    if form.validate_on_submit():
        article = Article(title=form.title.data, content=form.content.data)
        if Article.query.filter_by(title=form.title.data).first() is None:  # 文章不存在
            db.session.add(article)
            flash('发布成功')
        else:  # 文章已存在
            article = Article.query.filter_by(title=form.title.data).first()
            article.content = form.content.data
            db.session.add(article)
            # db.session.commit()
            flash('文章更新成功')
        form.title.data = ''
        form.content.data = ''
    return render_template('admin/index.html', form=form)


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            if user.check(form.password.data):
                login_user(user)
                return redirect(url_for('admin.index'))
            else:
                flash("用户名或者密码错误")
                return redirect(url_for('admin.login'))
        else:
            flash('没有你这个用户，请注册')
    return render_template('admin/login.html', form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经退出了。')
    return redirect(url_for('admin.login'))


@admin.route('/register', methods=['GET', 'POST'])
def register():
    global is_exist_admin
    form = RegistrationForm()
    if form.validate_on_submit() and not is_exist_admin:
        try:
            user = User(username=form.username.data, password=form.password.data)
            db.session.add(user)
            is_exist_admin = True
            flash('注册成功')
            return redirect(url_for('admin.login'))
        except:
            flash('帐号已存在')
            return redirect(url_for('admin.register'))
    else:
        flash('管理员已存在')
    return render_template('admin/register.html', form=form)
