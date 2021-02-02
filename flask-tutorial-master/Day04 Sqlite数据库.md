# Sqlite数据库

源代码: https://github.com/ltoddy/flask-tutorial

技术交流群:630398887(欢迎一起吹牛)

用到的数据库是sqlite，这个数据库不需要安装(因为这个数据库的运行是基于文件系统的)，只要你电脑能运行C语言就行（是个能开机的电脑就可以……）。

安装：
```
pip install flask-sqlalchemy
```
或者通过pycharm内置的pip安装

这里说一下数据库URL（待会要用到）。就是说阿，如果你要链接数据库，得先告诉程序数据库在哪，无论是local的或者remote的。URL就是那个数据库的位置。

|数据库引擎           |URL|
|-------------------|-----|
|SQLite(Unix)       |sqlite:////absolute/path/to/database|
|SQLite(Windows)    |sqlite:///c:/absolute/path/to/database|

不同的系统对于SQLite的URL是有一点不同的，我说一下原因，在Unix系统家族中，有一个根目录"/"，Unix系统是不分盘符的，也就是没有C盘，D盘之类的，所有东西都在根目录之下。而windows系统呢是分盘符的，比如你有东西在C盘，那么对于C盘来说，它的根目录也就是c:/所以说，对于这两个系统数据库URL的切换，只需要'/'与'c:/'互相转换一下就好了。

配置数据库：
```python
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
# 我们要把数据库放在当下的文件夹,这个basedir就是当下文件夹的绝对路径

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(basedir, 'data.sqlite')
# 这里注意看，写的是URI（统一资源标识符）
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
# SQLALCHEMY_COMMIT_TEARDOWN 因为数据库每次有变动的时候，数据改变，但不会自动的去改变数据库里面的数据，
# 只有你去手动提交，告诉数据库要改变数据的时候才会改变，这里配置这个代表着，不需要你手动的去提交了，自动帮你提交了。
# 待会会有演示
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

简单说一下数据库：
正规点的定义就是：数据库是长期存储在计算机内，大量有组织可共享的数据的集合。

简单点就是，比如你有一个database（数据库）,数据库中有很多表格，就像excel那样子。
表格中有每一列的名字（字段），用来标记每一列是存的什么信息。就这么简单，当然数据还会有些特殊的属性，比如primary key， unique， not null等等。


OK，我们来定义一下我们的表格。这个项目为了简单，只设立一个User表。用来之后的注册用的。

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 如果你学过数据库的话就知道我们一般通过id来作为主键，来找到对应的信息的,通过id来实现唯一性
    name = db.Column(db.String(64), unique=True)
```

下面将有一堆知识点，没空看的话就跳过去好了，等遇到了这方面的问题再来查看。
我复制的，太多了手打得累死我。

### 常见的SQLALCHEMY列类型

|类型名称	        |python类型	        |描述     |
|---------------|-------------------|-------|
|Integer	    |int	            |常规整形，通常为32位
|SmallInteger   |int	            |短整形，通常为16位
|BigInteger     |int或long	        |精度不受限整形
|Float	        |float	            |浮点数
|Numeric        |decimal.Decimal    |定点数
|String	        |str	            |可变长度字符串
|Text	        |str	            |可变长度字符串，适合大量文本
|Unicode        |unicode            |可变长度Unicode字符串
|Boolean        |bool	            |布尔型
|Date	        |datetime.date	    |日期类型
|Time	        |datetime.time	    |时间类型
|Interval       |datetime.timedelta |时间间隔
|Enum	        |str	            |字符列表
|PickleType	    |任意Python对象	    |自动Pickle序列化
|LargeBinary    |str                |二进制

### 常见的SQLALCHEMY列选项

|可选参数	    |描述|
|-----------|-----|
|primary_key|如果设置为True，则为该列表的主键
|unique     |如果设置为True，该列不允许相同值
|index      |如果设置为True，为该列创建索引，查询效率会更高
|nullable   |如果设置为True，该列允许为空。如果设置为False，该列不允许空值
|default    |定义该列的默认值


## 数据库操作
### 创建表
```
python blog.py shell
>>> from hello import db
>>> db.create_all()
```
### 删除表
```
db.drop_all()
```
### 插入行
```
#创建对象，模型的构造函数接受的参数是使用关键字参数指定的模型属性初始值。
admin_role = Role(name='Admin')
user_role = Role(name='User')
user_susan = User(username='susan', role=user_role)#role 属性也可使用,虽然它不是真正的数据库列,但却是一对多关系的高级表示。
user_john = User(username='john', role=admin_role)
#这些新建对象的 id 属性并没有明确设定,因为主键是由 Flask-SQLAlchemy 管理的。
print(admin_role.id)#None
#通过数据库会话管理对数据库所做的改动,在 Flask-SQLAlchemy 中,会话由 db.session 表示。
##首先，将对象添加到会话中
db.session.add(admin_role)
db.session.add(user_role)
db.session.add(user_susan)
db.session.add(user_john)
#简写：db.session.add_all([admin_role, user_role, user_john, user_susan])
##通过提交会话(事务)，将对象写入数据库
db.session.commit()
```
### 修改行
```
admin_role.name = 'Administrator'
db.session.add(admin_role)
session.commit()
```
### 删除行
```
db.session.delete(mod_role)
session.commit()
```

### 查询行
```
查询全部。Role.query.all()
条件查询（使用过滤器）。User.query.filter_by(role=user_role).all()
user_role = Role.query.filter_by(name='User').first()#filter_by() 等过滤器在 query 对象上调用,返回一个更精确的 query 对象。
```

### 常用过滤器

|过滤器	|说 明|
|--------|-------|
|filter()	|把过滤器添加到原查询上,返回一个新查询
|filter_by()|把等值过滤器添加到原查询上,返回一个新查询
|limit()	|使用指定的值限制原查询返回的结果数量,返回一个新查询
|offset()	|偏移原查询返回的结果,返回一个新查询
|order_by()	|根据指定条件对原查询结果进行排序,返回一个新查询
|group_by()	|根据指定条件对原查询结果进行分组,返回一个新查询

### 最常使用的SQLAlchemy查询执行函数

|方 法|	说 明|
|------|-------|
|all()	|以列表形式返回查询的所有结果
|first()|	返回查询的第一个结果,如果没有结果,则返回 None
|first_or_404()|	返回查询的第一个结果,如果没有结果,则终止请求,返回 404 错误响应
|get()	|返回指定主键对应的行,如果没有对应的行,则返回 None
|get_or_404()|	返回指定主键对应的行,如果没找到指定的主键,则终止请求,返回 404 错误响应
|count()	|返回查询结果的数量
|paginate()	|返回一个 Paginate 对象,它包含指定范围内的结果

OK,知识点到此为止。

我们来操作一下数据库:
更改这个路由

```python
@app.route('/', methods=['GET', 'POST'])
def index():
```

代码如下:

```python
@app.route('/', methods=['GET', 'POST'])
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
        return redirect(url_for('index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False))
```

注意看 db.session.add(user)。

假设没有

```
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
```

这行代码。

那么那行db.session.add(user)的后面需要加上db.session.commit()才可以把数据放到数据库中。

对应的 /templates/index.html 也要更改一下:

```jinja2
{% extends 'base.html' %}
{% import 'bootstrap/wtf.html' as wtf %}
{% block page_content %}
    <div class="page-header">
        <h1>Hello {% if name %}{{ name }}{% else %}stranger!{% endif %}</h1>
        {% if not known %}
            <p>Nice to meet you!</p>
        {% else %}
            <p>Happy to see you again!</p>
        {% endif %}
    </div>
    {{ wtf.quick_form(form) }}
{% endblock %}
```

说一下，如果你要运行项目，然后打开页面可能会出现一些SQLAlchemy的异常，这个时候，首先去看一下

```
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(basedir, 'data.sqlite')
```

这个，我们关心的是最后data.sqlite这个文件是否存在。
如果你没有发现这个文件的话，那么打开terminal(pycharm已经集成好了).

```
python3 blog.py shell
>>> from blog import *
>>> db # 这一行目的是看看db被添加进来了么。
<SQLAlchemy engine=sqlite:////home/me/PycharmProjects/blog/data.sqlite>
>>> db.drop_all()
>>> db.create_all()
```

这个样子你就会看到data.sqlite出现在你的文件夹中了。
