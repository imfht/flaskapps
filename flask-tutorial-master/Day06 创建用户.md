# 创建用户

源代码: https://github.com/ltoddy/flask-tutorial

技术交流群:630398887(欢迎一起吹牛)

写在前面的话:
如果你启动了项目,要去看本篇的内容,需要如下几个地址:
- localhost:5000/admin
- localhost:5000/admin/login
- localhost:5000/admin/register

还有就是,本篇我们数据库的设计改变了，所以在修改好app/models.py文件之后,要:
```python
$ python3 manage.py shell
>>> from manage import *
>>> db
<SQLAlchemy engine=sqlite:////home/me/PycharmProjects/blog/data.sqlite>
>>> db.drop_all()
>>> db.create_all()
>>> exit()
```

如果你启动项目之后，页面给出了一个sqlalchemy相关的异常，看看你有没有执行上面的语句。

OK，这次要好好说明一下蓝图的好处.

一般我们网上的一些网站都是可以用户登录的，通过用户名（邮箱或者手机号）和密码。
我们也不需要那么麻烦，只需要用户米和密码就够了。

我们需要更改一下 models.py 代码:

<small>app/models.py</small>
```python
from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 如果你学过数据库的话就知道我们一般通过id来作为主键，来找到对应的信息的,通过id来实现唯一性
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))

    def __repr__(self):
        return 'users表: id为:{}, name为:{}'.format(self.id, self.name)
```

其实就加上了 password 那一行.因为我们登录的时候需要帐号和密码这两样东西.

我们还需要处理一下我们的表单，毕竟我们需要注册和登录，都需要填写表单。

<small>app/admin/forms.py</small>
```python
from flask.ext.wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import PasswordField
from wtforms.validators import Required
from wtforms.validators import EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('用户名:', validators=[Required()])
    password = PasswordField('密码:', validators=[Required()])
    password2 = PasswordField('确认密码', validators=[Required(), EqualTo('password', message='两次密码不一致')])
    # 再这里, 一般来说你注册的时候都要求你输入两次相同的密码的,而且要求是一样的,所以我们可以使用wtforms帮我们集成好的EqualTo方法.
    # 那个message就是当你两次密码不一样的时候的提示信息
    submit = SubmitField('确认,提交')


class LoginForm(FlaskForm):
    username = StringField('用户名:', validators=[Required()])
    password = PasswordField('密码:', validators=[Required()])
    submit = SubmitField('确认,提交')
```

关于这两个表单，我曾经思考过:因为这两个表单中有相同的部分,我想提取出来:

```python
class BaseForm(FlaskForm):
    username = StringField('用户名:', validators=[Required()])
    password = PasswordField('密码:', validators=[Required()])
    submit = SubmitField('确认,提交')

class RegisterForm(BaseForm):
    password2 = PasswordField('确认密码', validators=[Required(), EqualTo('password', message='两次密码不一致')])

class LoginForm(BaseForm):
    pass
```

就像上面代码那样子,然而我否决了自己,这样子写大幅度的降低了可读性,而且,这个表单类,与HTML中的表单是一个一一对应的关系,所以最好不要提取一个父类来写.


写完这些,我们创建一下响应的蓝图:

<small>app/admin/\_\_init\_\_.py</small>

```python
from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import forms
from . import views
```

别忘了注册一下蓝图

<small>app/\_\_init\_\_.py</small>

```python
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'  # 这行代码就记住吧，我也不想解释了
login_manager.login_view = 'admin.login'  # 设置登录界面, 名为admin这个蓝本的login视图函数


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    # 这里我们 url_prefix='/admin， 这个样子我们访问admin蓝本中的路由的时候，就需要加上前缀：admin
    return app
```

这里注意一下啊:

```python
from flask.ext.login import LoginManager
login_manager = LoginManager()
login_manager.session_protection = 'strong'  # 这行代码就记住吧，我也不想解释了
login_manager.login_view = 'admin.login'  # 设置登录界面, 名为admin这个蓝本的login视图函数
```

我们需要有一个管理用户登录的东西—— LoginManager

还是要说一下蓝图，我们要做的这个blog，这个应用程序(app),他会有各个模块。举个例子，比如你去淘宝网页。
你会看到：比如主页各种商品，用户登录注册，银行卡绑定等等一大堆的模块。如果像最开始的那个样子，路由和视图函数全部是由那个app实例来做的话，就得把app添加到各个地方去，很麻烦，也很混乱。

采用蓝本，就相当于每个模块有了自己构件路由和视图函数的工具，然后再把蓝本注册到app中，这样就方便多了。
就比如，北方种植小麦，南方种植水稻，北方就专心种小麦，南方就专心种水稻。
如果你都想吃，那么等他们收割了，集中在一块就好了，差不多这个意思。

OK，我们来设计一下我们的视图函数。
考虑这么一件事情，比如你去知乎，如果你没有登录，它是要求你登录的。
也就是说：假设你没有登录，那么你去主页，就会重定向到登录界面。

这里顺便说一下，我们一般会把index.html当作主页，这是默认的。
比如我的技术博客, http://algo.site 和访问 http://algo.site/index.php 是一样的。

为了能够将你登录之后的状态记录下来，我们需要为我们的User模型添加点东西:

```python
from . import db
from . import login_manager
from flask.ext.login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 如果你学过数据库的话就知道我们一般通过id来作为主键，来找到对应的信息的,通过id来实现唯一性
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))

    def __repr__(self):
        return 'users表: id为:{}, name为:{}'.format(self.id, self.name)

    def check(self, password):
        return password == self.password


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

只是多继承了一个UserMixin类。
他帮我们提供了一些功能：比如判断是否登录，比如获取你的主键(id)，为了唯一标识用户，这一点很重要，因为就像一个大型网站，肯定会多人同时在新，如何去确认你，这里非常重要，靠的就是这个id。

还需要加上一个回调函数，就是为了识别出你来的。

OK，最后是视图函数：

<small>app/admin/views.py</small>

```python
from . import admin
from ..models import User
from .forms import LoginForm, RegistrationForm
from .. import db
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash
from flask.ext.login import current_user
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import login_required


@admin.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    return render_template('admin/index.html')


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
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, password=form.password.data)
            db.session.add(user)
            flash('注册成功')
            return redirect(url_for('admin.login'))
        except:
            flash('帐号已存在')
            return redirect(url_for('admin.register'))
    return render_template('admin/register.html', form=form)
```

讲一下这些视图函数中的业务逻辑。

- 第一个index():

    就是我们后台管理的那个页面，比如你把博客文章写好之后，在这里提交，然后在blog的主页显示出来。
    当然目前还没做好。
    顺便说一下,current_user.is_authenticated 这个东西，是一个标志的变量，用来标志你有没有登录。
    如果登录的，就是True，没登录就是False。
    在这里，如果你没有登录，那么index这个页面你是看不到的，会强行重定向到登录页面

- 第二个login():

    这个就是登录页面，当你提交表单之后，会去数据库查询，是否有你这个用户。我们这里有两层用于判断的if。

    第一层判断的if，用来判断数据库里有没有你这个用户，如果没有你这个用户，会给你一个提示信息。

    第二层判断的if，用来判断你密码是否正确，我们在User这个类中添加了check()这个方法。
    如果登录成功会跳转到后台的主页，没成功就提示密码错误。

- 第三个logout():

    这个就是用来用户退出用的。他被@login_required所保护着，什么意思呢？就是你如果没有登录的话，你去强行访问:localhost:5000/admin/logout这个页面的话，它会重定向到登录页面。这里我要说明一下，虽然代码写的是：return redirect(url_for('admin.login'))这个，但是实际上阿，如果你没有登录访问了这个logout视图，它其实是根据login_manager.login_view = 'admin.login'你的这个设置来重定向的。

- 最后register():
    我们在数据库设计中阿，那个username字段设置的是unique，也就是唯一，用户名有且仅有一个，如果你创建的用户已经在数据库中存在了，那么添加到数据库会报一个异常，所以用try except语句来处理异常.没什么好说的……

说点好玩的：你看阿，我们有了蓝图之后，从项目结构上看，一个蓝图对应一个文件夹，我们仅仅需要做的是，写好蓝图管辖下的路由就好，而不需要管其他蓝图的路由，这个样子，我们就把程序模块话了，每个模块各自有各自的功能，不会因为修改了这个模块而去影响其他模块，这个是非常好的一件事情，然后只需要最后的时候，把蓝本注册一下，把这些路由添加到应用中就好。


还有，

```python
bootstrap.init_app(app)
db.init_app(app)
login_manager.init_app(app)
```

这些东西，我们把app这个实例当作参数传了进去，有个技术叫依赖注入(也叫控制反转)，当app传进去之后，那么与app相关的数据也就传了进去，在比如bootstrap中，比如
```
{% import 'bootstrap/wtf.html' as wtf %}
```
他是怎么凭借一个名字：'bootstrap/wtf.html'来获得这个页面的，如果你是用的pycharm来写的话，软件会给你提示信息，说找不到这个模板的。很简单，我们把app给了bootstrap，然后bootstrap中就有了这个app，他识别了这个app，所以就可以用bootstrap了。

### **对了，相关的html页面我没有在文章中把源码放上，太占地方了，所以从源码那里复制一下好了。**
