# 使用Flasky-SQLAlchemy 管理数据库

 本文主要解决那本《Flask Web开发 基于Python的Web应用开发实战》
这本书坑不少，书是挺好的，但是你会踩不少坑，导致你会有很多bug，即使你复制的源代码。

先来一段代码
```python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +\
            os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/')
def index():
    return "Hello world"


if __name__ == '__main__':
    app.run()
```

注意，我在app.config中有一行是打了注释的。
如果加了注释：效果如下：

![](http://upload-images.jianshu.io/upload_images/3308539-54d3d5d412e9cb7f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

它会显示一个warning。一个警告

如果那一行去掉注释，效果如下：
![](http://upload-images.jianshu.io/upload_images/3308539-f982d77acc1f83ee.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

这样子警告就消失了。

接下来，为数据库建个表，简单起见，表中就两个字段，一个id，一个username，

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))


@app.route('/')
def index():
    u = User(username='zhangsan')
    return u.username
```

![](http://upload-images.jianshu.io/upload_images/3308539-550a78ad3bc385a5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

看上去还可以。
再换个方式。真正把用户数据(就是那个变量u)添加到数据库去.

```python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +\
            os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))


@app.route('/')
def index():
    u = User(username='zhangsan')
    db.session.add(u)
    return User.query.filter_by(username='zhangsan').first().username


if __name__ == '__main__':
#    db.drop_all()
#    db.create_all()
    app.run()
```

注意看在最下面，注释的那两行，如果注释掉的话，你去运行，会出现一个500的错误
![](http://upload-images.jianshu.io/upload_images/3308539-78fb52f569e0dcfa.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

这是你仔细观察目录中的文件，多了一个名字叫:data.sqlite的文件，然后你去查看这个文件的内容，
你会发现里面什么都没有。
原因很简单，因为数据库的表你根本就还没有创建呢，所在在最下面if里面的两行，是为了创建表用的。
估计大多数人被这个坑了。

当我们把注释解除之后.

![](http://upload-images.jianshu.io/upload_images/3308539-550a78ad3bc385a5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![](http://upload-images.jianshu.io/upload_images/3308539-c9ee5a051688429e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

这个样子就有东西了。


所以总的来说，当你去按照那个书学习的时候，如果打开localhost:5000之后出现SQLAlchemy的Error的时候
，先去看看有没有那个.sqlite文件(一般都有),然后去看看里面有没有东西，如果没有请按照如下方式:


这里假设你的db变量所在文件为:manage.py
```python
python3 manage.py shell

>>>from manage import db
>>>db.drop_all()
>>>db.create_all()
```
