# -*- coding:utf8 -*-
'''
index route.
'''
from flask import render_template, redirect, url_for, request, current_app, abort, flash
from . import main
from forms import PostForm
from ..comment.forms import CommentForm
from ..models import Permission, Post, Concern_posts, Comment, Tag, PostTag
from flask.ext.login import current_user, login_required
from .. import db
from .. import messages
import json
from datetime import datetime

# 定义路由函数
@main.route('/', methods=['GET', 'POST'])
def index():
    # 加载数据库所有文章
    page = request.args.get('page', 1, type=int)
    shows = request.args.get('shows')
    if current_user.is_authenticated and shows is not None and shows == 'recommend':
        pagination = current_user.recommend_posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False)
    elif current_user.is_authenticated and shows is not None and shows == 'concern':
        pagination = current_user.concern_posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False)
    elif current_user.is_authenticated and shows is not None and shows == 'home':
        pagination = current_user.posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False)
    else:
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination, shows=shows)

# 索引文章的链接
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    post.viewed_count = post.viewed_count + 1
    db.session.add(post)
    form = CommentForm()
    if not current_user.can(Permission.COMMENT):
        flash(messages.comment_cannot_access)
    else:
        if form.validate_on_submit():
            comment = Comment(author_id=current_user.id, body=form.comment.data, post=post, agree_count=0, disagree_count=0)
            db.session.add(comment)
            db.session.commit()
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', form=form, post=post, comments=comments, pagination=pagination)

# 编辑文章
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post.body = form.body.data
        post.title = form.title.data
        # 更新
        post.update_tags(form.tags.data)
        post.tags_txt = form.tags.data
        post.timestamp = datetime.utcnow()
        db.session.add(post)
        flash(messages.post_update_ok)
        return redirect(url_for('main.post', id=post.id))
    form.body.data = post.body
    form.title.data = post.title
    form.tags.data = post.tags_txt
    return render_template('edit.html', form=form)


# 编辑文章
@main.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = PostForm()
    if not current_user.can(Permission.WRITE_ARTICLES):
        abort(403)
    if form.validate_on_submit():
        post = Post(body=form.body.data, title=form.title.data, viewed_count=0, author=current_user._get_current_object(), tags_txt=form.tags.data)
        db.session.add(post)
        tags = form.tags.data.split(';')
        for tag in tags:
            ttag = Tag.query.filter_by(content=tag).first()
            if ttag is not None:
                ttag.refer_count = ttag.refer_count + 1
            else:
                ttag = Tag(content=tag, refer_count=1)
            post_tag = PostTag(post=post, tag=ttag)
            db.session.add(ttag)
            db.session.add(post_tag)
        flash(messages.post_create_ok)
        db.session.commit()
        return redirect(url_for('main.index', shows='home'))
    if None == form.body.data:
        form.body.data = '# 标题\n\n内容'
    if None == form.title.data:
        form.title.data = '输入博文名字'
    if None == form.tags.data:
        form.tags.data = '标签通过;隔开。'
    return render_template('edit.html', form=form)

# 编辑文章
@main.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMINISTER):
        abort(403)
    u = post.author
    Post.delete(post)
    return redirect(url_for('user.profile', username=u.username))

# 关注谋篇文章
@main.route('/concern/<int:id>')
@login_required
def concern(id):
    post = Post.query.get_or_404(id)
    is_concern = request.args.get('action')
    if is_concern == 'concern':
        if current_user.concern(post):
            flash(messages.concern_ok)
        else:
            flash(messages.concern_again_err)
    elif is_concern == 'unconcern':
        if current_user.unconcern(post):
            flash(messages.unconcern_ok)
        else:
            flash(messages.unconcern_again_err)
    else:
        pass
    return redirect(url_for('main.post', id=id))

@main.route('/remark/<int:id>')
@login_required
def remark(id):
    post = Post.query.get_or_404(id)
    attitude = int(request.args.get('attitude'))
    # 通过过滤条件
    if False == post.remark_it(attitude, current_user.id):
        flash(messages.post_remark_again_err)
    return redirect(url_for('main.post', id=post.id))

@main.route('/tags/<tagname>')
def tags(tagname):
    tag = Tag.query.filter_by(content=tagname).first()
    if tag is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = tag.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)

# 获取热门标签
@main.route('/json/tags/hot', methods=['GET', 'POST'])
def tags_hot():
    hots = Tag.query.order_by(Tag.refer_count.desc()).paginate(
        1, per_page=current_app.config['TAGS_HOT_NUM'],
        error_out=False).items
    hots_json = []
    for hot in hots:
        tmp = dict(name=hot.content, post_count=hot.refer_count)
        hots_json.append(tmp)
    hots_json = json.dumps(hots_json)
    rsp = dict(status='ok', err_code=10000)
    return render_template('json/tags.json', rsp=rsp, hots_json=hots_json)