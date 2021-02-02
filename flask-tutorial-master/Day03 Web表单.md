# Web表单

源代码: https://github.com/ltoddy/flask-tutorial

技术交流群:630398887(欢迎一起吹牛)

```
pip install flask-wtf
```

先看看一个普通的HTML页面的表单的样子:
```html
<form action="">
    <label>你叫什么名字：<input type="text"></label><br>
    <input type="button" value="提交">
</form>
```

![](http://img.vim-cn.com/32/11edeccf4a37843499eb0e699e6c2aa8a61e8c.png)

也就是说阿，在你要填写的框框前有一个提示的标语（label），然后有一个提交的按钮，按钮上写着提交俩字。

```python
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField

class NameForm(FlaskForm):
    name = StringField('你叫什么名字？') # 这里的'你叫什么名字？'就是对应的那个提示语
    # StringField() 就是那个输入的框框
    submit = SubmitField('提交') # 这里的'提交'对应着按钮的文字
```

先大体浏览一下下面两个表格，然后我在具体讲解怎么使用

### WTForms支持的HTML标准字段

|字段类型	            |说明  |
|-------------------|-----|
|StringField	    |文本字段|
|TextAreaField	    |多行文本字段|
|PasswordField	    |密码文本字段|
|HiddenField	    |隐藏文本字段|
|DateField	        |文本字段，值为datetime.date格式|
|DateTimeField	    |文本字段，值为datetime.datetime格式|
|IntegerField	    |文本字段，值为整数|
|DecimalField	    |文本字段，值为decimal.Decimal|
|FloatField	        |文本字段，值为浮点数|
|BooleanField	    |复选框，值为True和False|
|RadioField	        |一组单选框|
|SelectField	    |下拉列表|
|SelectMultipleField|下拉列表，可选择多个值|
|FileField	        |文件上传字段|
|SubmitField	    |表单提交按钮|
|FormField	        |把表单作为字段嵌入另一个表单|
|FieldList	        |一组指定类型的字段|

### WTForms验证函数

|验证函数       |	说明|
|--------------|------|
|Email	       |验证电子邮件地址|
|EqualTo	   |比较两个字段的值，常用于要求输入两次密码进行确认的情况|
|IPAddress	   |验证IPv4网络地址|
|Length	       |验证输入字符串的长度|
|NumberRange   |验证输入的值在数字范围内|
|Optional	   |无输入值时跳过其他验证函数|
|Required	   |确保字段中有数据|
|Regexp	       |使用正则表达式验证输入值|
|URL	       |验证URL|
|AnyOf	       |确保输入值在可选值列表中|
|NoneOf	       |确保输入值不在可选列表中|

### 把表单加入到页面中去:

顺便提一句，之前的那个hello_world函数，我把它改名为index了。
先看我们的html页面：

<small>templates/index.html</small>
```html
{% extends 'base.html' %}
{% import 'bootstrap/wtf.html' as wtf %}
{% block page_content %}
    <div class="page-header">
        <h1>Hello {% if name %}{{ name }}{% else %}stranger!{% endif %}</h1>
    </div>
    {{ wtf.quick_form(form) }}
{% endblock %}
```

第二行：

```
{% import 'bootstrap/wtf.html' as wtf %}
```

bootstrap为我们集成好了一个宏（理解成函数就好了），它可以很方便的把我们的表单类(刚才的NameForm)渲染成表单。

再看下面:

```
{% <h1>Hello {% if name %}{{ name }}{% else %}stranger!{% endif %}</h1> %}
```

如果有名字近来，那么显示名字，没有名字的话就显示stranger（陌生人）。

再来看一下视图函数：

<small>blog.py</small>
```python
class NameForm(FlaskForm):
    name = StringField('你叫什么名字', validators=[Required()])
    submit = SubmitField('提交')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    name = None
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('index.html', name=name, form=form)
```

注意看，和刚才有差别。

第一个是没有那个validators=[Required()]这一部分的，这段是什么意思呢，就是说你在框框中填写的内容是有要求的，这个Required()的要求是，框框中的内容不为空才可以提交。
如果你什么都没写，然后提交，就会出现：
![](http://img.vim-cn.com/87/b1b868d603ff4c29c21be4bd5351a397b2d2e5.png)

类似这样的情况。具体看每个人电脑的具体实现了。
还有一点，表单的提交要通过POST方法，这里不再多余说了，具体去看HTTP协议。

但是这个页面还是有问题的，当你按下F5去刷新页面的时候，会给你个提示：问你表单是不是要重新提交一下。
因为页面刷新会向浏览器重新发送最后一个请求，这里的请求是提交表达，基于这个原因，我们利用重定向，来改成GET请求。

<small>blog.py</small>
```python
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', name=session.get('name', None), form=form)
```
这里我用到了一个东西：session（会话），它会记住上下文，把数据存储在这个session中。怎么理解呢？
浏览器是一个傻子，他只能记住最后发生的一件事情，这个session就是为了强行让浏览器记住一些东西。
还用到了redirect和url_for这两个组合,url_for便于我们生成url，当然那一行代码你也可以写成:

```python
redirect('/')
```

因为就是要回到主页嘛，主页地址就是'/'，但是随着程序日益的复杂，你不可能完全掌握所有的地址，所以我们通过url_for来获得地址，url_for('index')注意看括号中的参数内容'index'对应着视图函数index()的名字。也就是说重新定向到这个函数映射的页面上。

看一下完整代码:

<small>blog.py</small>
```python
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import Required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a string' # 这一行是必须要加上的，为了防止CRSF攻击
bootstrap = Bootstrap(app)
manager = Manager(app)


class NameForm(FlaskForm):
    name = StringField('你叫什么名字', validators=[Required()])
    submit = SubmitField('提交')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', name=session.get('name', None), form=form)


@app.route('/<username>')
def user(username):
    return render_template('user.html', name=username)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    manager.run()
```

再介绍一点更人性化的东西：

### Flash消息：
有些时候，当你作出了改动的时候，最好有个东西来提醒你:flash

<small>blog.py</small>
```python
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('你更改了名字')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', name=session.get('name', None), form=form)
```

需要再更改一下我们的模板，让flash消息显示出来

<small>templates/base.html</small>
```jinja2
{% block content %}
    {% for message in get_flashed_messages() %}
        <div class="alert alert-info">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            {{ message }}
        </div>
    {% endfor %}
    <div class="container">
        {% block page_content %}{% endblock %}
    </div>
{% endblock %}
```

赶快去运行程序尝试提交表单看看效果吧.
