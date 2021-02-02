# 难说再见

源代码: https://github.com/ltoddy/flask-tutorial

技术交流群:630398887(欢迎一起吹牛)

写在前面的话：
如果要运行这次的代码，请先:
```
$ python3 manage.py shell
>>> from manage.py import *
>>> db.drop_all()
>>> db.create_all()
>>> exit()
```

因为我已经注册了用户了。

到目前为止，blog还是有很多问题的：

- 数据库建模方面，没有使用外键，也就是说没有一对多或者多对一的关系。也就是说，对于目前的blog，如果你注册了多个用户，那么这些用户对于所有文章是共用的。而不是各自用户有各自的文章 —— 如何解决，当然你也可以使用外键来链接两个表实现，或者我们就只允许一个用户(管理员)的存在，私人使用。

- 我们的后台功能太欠缺。目前只有一个发布功能，其实还需要：
    - 文章的修改
    - 文章的删除

- 我们没有设置文章的类型，所以目前无法给文章分类，其实也很好解决，在app/models.py的文章模型中加入一个type字段就好。

第一个问题，简单的解决方法:在config.py中加一个全局变量(bool类型)，初始值为False，表示目前没有用户注册，当第一个用户注册之后，这个变量设为True，表示已经有一个用户注册了，那么就可以不再让第二个用户注册了。

<small>config.py</small>

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))

is_exist_admin = False


class Config:
    SECRET_KEY = 'a string'
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass
```

多了这个: is_exist_admin = False


```python
from config import is_exist_admin

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
```

第二个问题：

先解决添加文章的修改功能，我们可不可以这样子，把发布文章和更新文章视作同一种操作。
我们将发布和更新文章这两个功能合二为一，怎么说呢。当你去发布文章的时候，根据标题去查询数据库有没有这篇文章，如果没有这篇文章，那么就在数据库中添加这个信息，如果有这篇文章，那么就去更改数据库这条信息的内容。

<small>app/admin/views</small>
```python
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
```

最后是删除文章：这里我就不写了，我相信你可以自己做到。

### 说点额外话:
一个网站构成的,
- 用户看到的界面（前端）
- 后端表单验证+数据库

前端从来不是问题，因为毕竟你去百度可以搜索到各种各样炫酷的模板。
后端，这是核心。数据的处理在这里。
