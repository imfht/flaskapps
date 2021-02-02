# 大型程序结构

源代码: https://github.com/ltoddy/flask-tutorial

技术交流群:630398887(欢迎一起吹牛)

文中提到的狗书,就是《Flask Web开发 基于Python的Web应用开发实战》, 看过的人都是到,这本书坑挺多的.

![](http://img.vim-cn.com/cb/05f30904d7473ca2cabffd6f7602f389927559.png)

就是这本,反正大家都叫狗书,我也就跟着叫了……

参照狗书的内容,以及响应Dijkstra的模块化程序设计,我们这次要改一下程序结构,做一次大手术.

本篇会好好的说明一下蓝本(也叫蓝图).

蓝图简单一点就是,我们之前的程序不都是有一个Flask的实例

> app = Flask(\_\_name\_\_)

也就是这个变量app,它可以来定义路由.蓝图就是可以将路由分门别类,然后在组合在一起.
不懂没关系,往下看.

我们需要重新设置一下项目结构:

```
.
├── app
│   ├── admin
│   │   ├── errors.py
│   │   ├── forms.py
│   │   ├── __init__.py
│   │   └── views.py
│   ├── __init__.py
│   ├── main
│   │   ├── forms.py
│   │   ├── __init__.py
│   │   └── views.py
│   ├── models.py
│   ├── static
│   └── templates
│       ├── 404.html
│       ├── 500.html
│       ├── admin
│       │   ├── login.html
│       │   └── register.html
│       ├── base.html
│       ├── index.html
│       └── user.html
├── config.py
├── manage.py
```
差不多是这个样子的.

- Flask 程序一般都保存在名为app的包中.
- config.py 保存着配置
- manage.py 用于启动项目

这里说明一下python 的包(package),从目录结构上看,python的package有两部分组成： 文件夹和__init__.py 文件. 正是因为__init__.py 的存在 python编译器才会把那个文件夹当作是一个python的包来看待.  而那个 __init__.py 的效果就是, 能够有一个与包名字相同的文件. 什么意思呢？

比如 我们有一个名字为 main 的包, 那么

```python
from main import *
```

这行代码中,从main包中import所有的东西,你想啊,main是个包,import进来是啥？？？ 其实阿,是import进来的是__init__.py中的内容.

把原先那个blog.py中的东西复制一下就好了.

<small>config.py</small>
```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'a string'
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_COMMIT_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

```

仿照狗书,创建一个程序工厂函数. 设计模式中有一个模式叫做:工厂模式,比如你需要一个东西,但这个东西你需要配置很多,这样你就可以用到工厂模式,在把配置(比如汽车厂,把各个零件组装起来)的活交给工厂,那么工厂出来的产品就是好的产品.这样可以降低程序的耦合度,怎么理解呢,如果这个产品是坏的,那么你也不需要到处去程序的代码,只需要去那个工厂的程序中去寻找bug就好了.

### 程序工厂函数:
说一下工厂函数,我们之前单个文件开发程序很方便,但却有个很大的缺点,因为程序在全局作用中创建,所以无法动态修改配置.运行脚本时,实例已经创建,再修改配置为时已晚,解决问题的方法就是延迟创建程序实例,把创建过程移到可显式调用的工厂函数中.

<small>app/\_\_init\_\_.py</small>
```python
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)

    return app
```

看一下这段代码,我们的bootstrap和db实例,先于app创建,app的创建只能调用了create_app()函数之后才创建.

### 蓝图

Flask 中的蓝图为这些情况设计:
- 把一个应用分解为一个蓝图的集合。这对大型应用是理想的。一个项目可以实例化一个应用对象，初始化几个扩展，并注册一集合的蓝图。
- 以 URL 前缀和/或子域名，在应用上注册一个蓝图。 URL 前缀/子域名中的参数即成为这个蓝图下的所有视图函数的共同的视图参数（默认情况下）。
- 在一个应用中用不同的 URL 规则多次注册一个蓝图。
- 通过蓝图提供模板过滤器、静态文件、模板和其它功能。一个蓝图不一定要实现应用或者视图函数。
- 初始化一个 Flask 扩展时，在这些情况中注册一个蓝图。

蓝图问题,最后总结.往下看.

在蓝本中定义的路由处于休眠状态,直到蓝本注册到程序上后,路由才真正成为程序的一部分.

#### 创建蓝本:
<small>app/main/\_\_init\_\_</small>
```python
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
```

蓝图是通过实例化Blueprint类对象来创建的。这个类的构造函数接收两个参数：蓝图名和蓝图所在的模块或包的位置。与应用程序一样，在大多数情况下，对于第二个参数值使用Python的__name__变量即可。

应用程序的路由都保存在app/main/views.py模块内部，而错误处理程序则保存在app/main/errors.py中。导入这些模块可以使路由、错误处理与蓝图相关联。重要的是要注意，在app/init.py脚本的底部导入模块要避免循环依赖，因为view.py和errors.py都需要导入main蓝图。

### 注册蓝图:
<small>app/\_\_init\_\_.py</small>
```python
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
```

> app.register_blueprint(main_blueprint)

通过register_blueprint方法将蓝图注册进来.

<small>app/main/errors.py</small>
```python
from flask import render_template

from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
```

<small>app/main/views.py</small>
```python
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for

from . import main
from .forms import NameForm
from ..models import User
from .. import db


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data)
        if user is None:
            user = User(name=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.index'))
        # 这里注意一下,我们这里要写main.index,因为我们这个视图函数隶属于main这个蓝本,
        # main.index是他完整的名字.
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False))
```

<small>app/main/forms.py</small>
```python
from flask.ext.wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(FlaskForm):
    name = StringField('你叫什么名字', validators=[Required()])
    submit = SubmitField('提交')
```

<small>manage.py</small>
```python
from flask.ext.script import Manager

from app import create_app, db

app = create_app()
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
```

我们运行一下:
打开Pycharm为我们集成好的终端(Terminal)
```
python3 manage.py shell
>>> from manage import *
>>> db
<SQLAlchemy engine=sqlite:////home/me/PycharmProjects/blog/data.sqlite>
>>> db.drop_all()
>>> db.create_all()
>>> exit()
```
先把我们的表重新创建一下,因为表已经移动位置了.

然后

> python3 manage.py runserver

就可以看到程序正常运行了.

好像看不出蓝本有啥用……好吧。
现在还看不出,下一篇就确实看的出来了,因为我们要把后台搭建好,然后在后台把博客文章提交上去,然后文章存到数据库里面,然后数据有了,在前端把数据显示出来.


> 你的笔记本上有很多接口：USB、电源接口、SD卡槽、耳机孔、HDMI（可插拔视图）等等；隔壁老王的电脑，就一type-C口（蓝图接口），其他的接口只能通过type-C的扩展坞（在蓝图中添加url规则）再接到电脑上（注册蓝图）。老王下班，直接拔了那一根type-C走人（取消注册蓝图），而你要拔四五根线，这时候你就发现了这根type-C的方便，甚至当某个外接设备出问题（业务逻辑需要修改）时，你只需要在外接设备与那个拓展坞（蓝图中）之间修复，基本没你电脑（主程序）什么事，因为它降低了其他外接设备与你电脑的耦合。
