# -*- coding:utf8 -*-
'''
Add database models.
'''
from . import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from datetime import datetime

# 使用flask-login模块自动加载用户信息
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 模型字典，用于向外展示数据库模型
tables = {}

# 动态更新模型字典的修饰器
# 不需要改变类或者函数的行为，在一些处理以后，直接返回好了，不要包装函数了
def addModel(model):
    tables[model.__name__] = model
    return model

# 建立关注的关联模型
@addModel
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, index=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 建立用户和关注着博客的多对多关系模型
@addModel
class Concern_posts(db.Model):
    __tablename__ = 'concern_posts'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 评论主要是 对文章评论、对评论进行评论，这些都是文本式评论，还有一种是态度评论，比如赞同、反对等
@addModel
class Remark_Attitude:
    AGREE_WITH = 0x01
    DISAGREE_WITH = 0x02
    # 扩展

@addModel
class Remark(db.Model):
    __tablename__ = 'remarks'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), index=True)
    attitude = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@addModel
class RemarkPost(db.Model):
    __tablename__ = 'remarkposts'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)
    attitude = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 子评论表，用来表示对一篇文章的评论层级，层级不超过2，评论的自引用
@addModel
class SubComment(db.Model):
    __tablename__ = 'subcomment'
    id = db.Column(db.Integer, primary_key=True, index=True)
    for_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), index=True)
    from_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), index=True)

# 增加与博文多对一关系、与用户多对一关系的评论系统
@addModel
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    agree_count = db.Column(db.Integer, default=0)
    disagree_count = db.Column(db.Integer, default=0)
    body = db.Column(db.Text)

    # 子评论
    subcomments = db.relationship('SubComment', foreign_keys=[SubComment.for_comment_id], backref=db.backref('comment', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')

    def obtain_subcomments(self):
        return Comment.query.join(SubComment, SubComment.for_comment_id==Comment.id).filter(SubComment.for_comment_id==self.id)

    # 简评  态度评论
    remarks = db.relationship('Remark', foreign_keys=[Remark.comment_id], backref=db.backref('comment', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')

    def remark_count(self, type):
        # return Remark.query.filter_by(comment_id=self.id, attitude=type).count()
        if Remark_Attitude.AGREE_WITH == type:
            return self.agree_count
        elif Remark_Attitude.DISAGREE_WITH == type:
            return self.disagree_count
        else:
            return 0

    def remark_it(self, type, user_id):
        remark = Remark.query.filter_by(comment_id=self.id, owner_id=user_id).first()
        if remark is not None:
            return False
        if Remark_Attitude.AGREE_WITH == type or Remark_Attitude.DISAGREE_WITH == type:
            remark = Remark(comment_id=self.id, owner_id=user_id, attitude=type)
            db.session.add(remark)
            if Remark_Attitude.AGREE_WITH == type:
                self.agree_count = self.agree_count + 1
            else:
                self.disagree_count = self.disagree_count + 1
            return True
        else:
            return False

# USer model
@addModel
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 每个用户的email是唯一的，只能通过数据库删，否则终身不变
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # 文章的反向引用
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 更新用户登录时间
    def ping(self):
        self.last_seen = self.member_since
        self.member_since = datetime.utcnow()
        db.session.add(self)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 存储密码的散列值，不存储用户密码，为了保护用户密码的隐私性
    password_hash = db.Column(db.String(64))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 邮箱验证是否有效
    confirmed = db.Column(db.Boolean, default=False)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    @staticmethod
    def parse_confirm_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return data.get('confirm')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 添加权限验证
    def can(self, permissions):
        return self.role is not None and (self.role.permission & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    # 用户图像，存储用户头像的url，而非二进制格式
    avatar_url = db.Column(db.String(100), unique=True, index=True)
    # 生成avatar的hashurl，使用http://www.gravatar.com/avatar的生成头像的服务
    # 计算md5是计算密集型，会占用大量cpu，一般初始化新用户时，会执行一次
    def generate_avatar_url(self):
        # self.avatar_url = 'https://www.gravatar.com/avatar/'+hashlib.md5(self.email.encode('utf-8')).hexdigest()
        total = 0
        for i in range(1, len(self.email)):
            total = total + ord(self.email[i])
        self.avatar_url = '/static/avatar/avatar{0}.png'.format(total%200)

    # 生成不同尺寸的url，这时经常被调用
    def avatar_url_auto(self, size=100, default='idention', rating='g'):
        # return '{0}?s={1}&d={2}&r={3}'.format(self.avatar_url, size, default, rating)
        return self.avatar_url

    # 定义索引和反向索引
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    # 与关注相关的操作函数
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None
    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None
    @property
    def recommend_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    #定义关注着文章的反向引用
    concerns = db.relationship('Concern_posts', foreign_keys=[Concern_posts.user_id], backref=db.backref('user', lazy='joined'),
                    lazy='dynamic', cascade='all, delete-orphan')

    @property
    def concern_posts(self):
        return Post.query.join(Concern_posts, Concern_posts.post_id==Post.id)

    def concern(self, post):
        if not self.is_concerning(post):
            c = Concern_posts(user=self, post=post)
            db.session.add(c)
            return True
        else:
            return False
    def unconcern(self, post):
        c = self.concerns.filter_by(post_id=post.id).first()
        if c:
            db.session.delete(c)
            return True
        else:
            return False

    def is_concerning(self, post):
        return self.concerns.filter_by(post_id=post.id).first() is not None

    # 添加评论的反向引用
    comments = db.relationship('Comment', foreign_keys=[Comment.author_id], backref='author', lazy='dynamic')

    # 简评  态度评论
    remarks = db.relationship('Remark', foreign_keys=[Remark.owner_id], backref=db.backref('owner', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')

    def remark_count(self, type):
        return Remark.query(owner_id=self.id, attitude=type).count()

    # 简评  态度评论
    remarkposts = db.relationship('RemarkPost', foreign_keys=[RemarkPost.owner_id], backref=db.backref('owner', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')

    def remarkPost_count(self, type):
        return RemarkPost.query(owner_id=self.id, attitude=type).count()

    @staticmethod
    def insert_Administartor():
        role = Role.query.filter_by(name='Administrator').first()
        if role is None:
            raise Exception('you should run Role.insert_roles()!!')
        user = User(username=current_app.config['ADMIN_USERNAME'], email=current_app.config['ADMIN_EMAIL'], role=role, password=current_app.config['ADMIN_PASSWORD'])
        user.generate_avatar_url()
        db.session.add(user)
        db.session.commit()

    # 匿名用户很特殊，由于username、email、id等不会重复，所以只有一个属性那就是名字，主要用于匿名用户评论的，没有其他用途
    @staticmethod
    def insert_Anonymous():
        role = Role.query.filter_by(name='User').first()
        if role is None:
            raise Exception('you should run Role.insert_roles()!!')
        user = User(username='Anonymous', role=role)
        db.session.add(user)
        db.session.commit()
    @property
    def is_anonymous(self):
        return False

    @staticmethod
    def delete(user):
        # 删除用户的评论
        for comment in user.comments:
            db.session.delete(comment)
        # 删除用户的文章
        for post in user.posts:
            Post.delete(post)
        db.session.delete(user)

    def __repr__(self):
        return '<User %r>' % self.username

# 为了保证一致性，添加一个匿名用户，由于系统支持匿名用户评论，所以支持id和username属性，不支持别的属性会报错
class AnonymousUser(AnonymousUserMixin):
    @property
    def id(self):
        anonymous_user = User.query.filter_by(username='Anonymous').first()
        if anonymous_user is None:
            raise Exception('please run User.insert_Anonymous()!!!')
        return anonymous_user.id

    @property
    def username(self):
        anonymous_user = User.query.filter_by(username='Anonymous').first()
        if anonymous_user is None:
            raise Exception('please run User.insert_Anonymous()!!!')
        return anonymous_user.username

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_anonymous(self):
        return True

# 向flask-login管理添加默认的匿名类
login_manager.anonymous_user = AnonymousUser

# 使用权限来管理角色，同时通过一对多的关系，来对应相应用户
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_ARTICLES = 0x08
    MODERATE_USERS = 0x10
    ADMINISTER = 0xff

# 角色数据库，用于分配权限
@addModel
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permission = db.Column(db.Integer)
    users = db.RelationshipProperty('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_ARTICLES, False),
            'Administrator': (0xff, False)
        }
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name = role_name)
            role.permission = roles[role_name][0]
            role.default = roles[role_name][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

@addModel
class PostTag(db.Model):
    __tablename__ = 'posttags'
    id = db.Column(db.Integer, primary_key=True, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), index=True)

@addModel
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, index=True)
    content = db.Column(db.String(10))
    refer_count = db.Column(db.Integer, default=0)
    posttags = db.relationship('PostTag', foreign_keys=[PostTag.tag_id], backref=db.backref('tag', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')

    @property
    def posts(self):
        return Post.query.join(PostTag, PostTag.post_id==Post.id).filter(PostTag.tag_id==self.id)

@addModel
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, index=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    #定义关注着文章的反向引用
    concern_users = db.relationship('Concern_posts', foreign_keys=[Concern_posts.post_id], backref=db.backref('post', lazy='joined'),
                    lazy='dynamic', cascade='all, delete-orphan')

    def is_concerned_by(self, user):
        return self.concern_users.filter_by(user_id=user.id).first() is not None


    # 添加评论的反向引用
    comments = db.relationship('Comment', foreign_keys=[Comment.post_id], backref='post', lazy='dynamic')

    # 简评  态度评论
    remarkposts = db.relationship('RemarkPost', foreign_keys=[RemarkPost.post_id], backref=db.backref('post', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')

    def remarkPost_count(self, type):
        return RemarkPost.query.filter_by(post_id=self.id, attitude=type).count()

    viewed_count = db.Column(db.Integer)
    posttags = db.relationship('PostTag', foreign_keys=[PostTag.post_id], backref=db.backref('post', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')

    @property
    def tags(self):
        return Tag.query.join(PostTag, PostTag.tag_id==Tag.id).filter(PostTag.post_id==self.id)

    def update_tags(self, new_tags):
        old_tags = self.tags_txt.split(';')
        new_tags = new_tags.split(';')
        # 建立新标签
        for tag in new_tags:
            # 检查标签是否有增删的情况
            if tag not in old_tags:
                tTag = Tag.query.filter_by(content=tag).first()
                if tTag is None:
                    tTag = Tag(content=tag, refer_count=1)
                    post_tag = PostTag(post=self, tag=tTag)
                    db.session.add(tTag)
                    db.session.add(post_tag)
                else:
                    tPost_tag = PostTag.query.filter_by(tag_id=tTag.id, post_id=self.id).first()
                    if tPost_tag is None:
                        post_tag = PostTag(post=self, tag=tTag)
                        tTag.refer_count = tTag.refer_count + 1
                        db.session.add(post_tag)
                    else:
                        tTag.refer_count = tTag.refer_count - 1
                        db.session.delete(tPost_tag)
                    db.session.add(tTag)
        # 删除就标签
        for tag in old_tags:
            if tag not in new_tags:
                tTag = Tag.query.filter_by(content=tag).first()
                tPost_tag = PostTag.query.filter_by(tag_id=tTag.id, post_id=self.id).first()
                tTag.refer_count = tTag.refer_count - 1
                db.session.delete(tPost_tag)
                db.session.add(tTag)

    # 冗余信息
    tags_txt = db.Column(db.String(128))
    agree_count = db.Column(db.Integer, default=0)
    disagree_count = db.Column(db.Integer, default=0)

    title = db.Column(db.String(128))

    def remark_count(self, type):
        # return Remark.query.filter_by(comment_id=self.id, attitude=type).count()
        if Remark_Attitude.AGREE_WITH == type:
            return self.agree_count
        elif Remark_Attitude.DISAGREE_WITH == type:
            return self.disagree_count
        else:
            return 0

    def remark_it(self, type, user_id):
        remark = RemarkPost.query.filter_by(post_id=self.id, owner_id=user_id).first()
        if remark is not None:
            return False
        if Remark_Attitude.AGREE_WITH == type or Remark_Attitude.DISAGREE_WITH == type:
            remark = RemarkPost(post_id=self.id, owner_id=user_id, attitude=type)
            db.session.add(remark)
            if Remark_Attitude.AGREE_WITH == type:
                self.agree_count = self.agree_count + 1
            else:
                self.disagree_count = self.disagree_count + 1
            return True
        else:
            return False

    @staticmethod
    def delete(post):
        # 删除所有的评论
        for comment in post.comments:
            db.session.delete(comment)
        # 删除文章，不用管remark，因为是关联表在建立引用关系时，使用cascade='all, delete-orphan' 属性让sqlalchemy自动处理其关系
        tags = post.tags_txt.split(';')
        # 更新标签数量
        for tag in tags:
            tTag = Tag.query.filter_by(content=tag).first()
            tTag.refer_count = tTag.refer_count - 1
            db.session.add(tTag)
        db.session.delete(post)

    # 文章的摘要，默认取第一段落内容
    @property
    def abstarct(self):
        end = self.body.find('##')
        if end > -1 and end < current_app.config['POSTS_ABSTRACT_NUM']:
            return self.body[:end]
        end = self.body.find('```')
        if end > -1 and end < current_app.config['POSTS_ABSTRACT_NUM']:
            return self.body[:end]
        return self.body[:current_app.config['POSTS_ABSTRACT_NUM']]

    def __repr__(self):
        return '<Post %r>' % self.title

