# Jinja2模板引擎, 使用Twitter Bootstrap

源代码: https://github.com/ltoddy/flask-tutorial

技术交流群:630398887(欢迎一起吹牛)

有些地方没看懂没关系，坚持往下看，下面会有演示代码来说明。

上一篇中如下代码
```python
@app.route('/')
def hello_world():
    return 'Hello World!'
```
这个样子返回一个字符串，很不爽，能不能直接返回一个HTML页面，当然可以。

在templates文件夹下新建一个index.html

<small>templates/index.html</small>
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Just for fun</title>
</head>
<body>

<h1>Hello World</h1>

</body>
</html>
```
<small>blog.py</small>
```python
from flask import render_template
#...
@app.route('/')
def hello_world():
    return render_template('index.html')
```
这个样子就直接把那个index.html页面显示了出来.

## Jinja2模板引擎
### 渲染模板
在blog.py的def user(username) 这个函数中,如果我们想把那个username传入html页面怎么办呢?
在templates文件夹下新建user.html

<small>templates/user.html</small>
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Just for fun</title>
</head>
<body>

<h1>Hello {{ name }}.</h1>

</body>
</html>
```
视图函数user()返回的响应中包含一个使用变量表示的动态部分.
<small>blog.py</small>
```python
@app.route('/<username>')
def user(username):
    return render_template('user.html', name=username)
```
注意看这里的对应关系,在return那里,render_template接受了如下两个部分:

- 'user.html' 这个是要展现的页面名字,页面要放在templates文件夹下,jinja2引擎会自动去templates文件夹寻找此文件.
- 第二部分就是user.html中所需要的参数,这里可以有很多个参数,下文将会看到.在这里,name=username,左边的name表示参数名,就是模板中使用的占位符,右边的username是当前作用域中的变量.

### 变量
刚才使用的{{ name }}结构表示一个变量,它是一个特殊的占位符,告诉模板引擎这个位置的值从渲染模板时使用的数据中获取.
Jinja2能识别所有类型的变量,甚至是一些特殊的类型:例如列表,字典和对象.
e.g.
```
A value from a dictionary: {{ mydict['key'] }}.
A value from a list: {{ mylist[3] }}.
A value from a list, with a variable index: {{ mylist[myintvar] }}
A value from a object's method: {{ myobj.somemethod() }}.
```

Jinja2另外也提供了叫 _过滤器_ 的东西，但是不怎么用，这里就不再说明了。

[Jinja2过滤器完整文档](http://jinja.pocoo.org/docs/templates/#builtin-filters)


下面是一些知识的介绍,了解一下就好.
### 控制结构
#### 条件控制结构语句:
```jinja2
{% if user %}
    Hello, {{ user }}!
{% else %}
    Hello, Stranger!
{% endif %}
```
#### 循环控制结构
```jinja2
<ul>
    {% for comment in comments %}
        <li>comment</li>
    {% endfor %
</ul>
```

需要在多出重复使用的模板代码片段可以写入单独的文件,再包含在所有模板中,以避免重复:
```jinja2
{% include 'common.html' %}
```
另一种重复使用代码的强大方式是模板继承.
首先创建一个名为base.html的模板
```jinja2
<html lang="en">
<head>
    {% block head %}
        <title>{% block title %}{% endblock %} - My Application</title>
    {% endblock %}
</head>
<body>
{% block body %}
{% endblock %}
</body>
</html>
```
block标签定义的元素可在衍生模板中修改.例如
```jinja2
{% extends 'base.html' %}
{% block title %}Index{% endblock %}
{% block head %}
    {{ super() }}
    <style>
    </style>
{% endblock %}
{% block body %}
<h1>Hello, World!</h1>
{% endblock %}
```
block标签定义的元素可以在衍生的模板中修改.
extends指令声明这个模板衍生自base.html.在extends指令之后,基模板中的3个块被重新定义,模板引擎会将其插入适当的位置.

## 使用Flask-Bootstrap集成Twitter Bootstrap
如果电脑上有pip的可以:
```
pip install flask-bootstrap
```
没有的就如上篇文章那样,通过Pycharm自动帮你安装.
Bootstrap CSS样式库,简单点理解就是你获得了一大堆化妆品(定制好的,而非按照自己想法定制的样子),可以有选择的去使用.

初始化Flask-Bootstrap:
```python
from flask_bootstrap import Bootstrap
# ...
bootstrap = Bootstrap(app)
```
待会要通过继承Bootstrap的base.html页面来实现模板的复用.
先看看bootstrap的base.html为我们提供了什么:
```jinja2
{% block doc -%}
    <!DOCTYPE html>
    <html{% block html_attribs %}{% endblock html_attribs %}>
    {%- block html %}
        <head>
            {%- block head %}
                <title>{% block title %}{% endblock title %}</title>

                {%- block metas %}
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                {%- endblock metas %}

                {%- block styles %}
                    <!-- Bootstrap -->
                    <link href="{{ bootstrap_find_resource('css/bootstrap.css', cdn='bootstrap') }}" rel="stylesheet">
                {%- endblock styles %}
            {%- endblock head %}
        </head>
        <body{% block body_attribs %}{% endblock body_attribs %}>
        {% block body -%}
            {% block navbar %}
            {%- endblock navbar %}
            {% block content -%}
            {%- endblock content %}

            {% block scripts %}
                <script src="{{ bootstrap_find_resource('jquery.js', cdn='jquery') }}"></script>
                <script src="{{ bootstrap_find_resource('js/bootstrap.js', cdn='bootstrap') }}"></script>
            {%- endblock scripts %}
        {%- endblock body %}
        </body>
    {%- endblock html %}
    </html>
{% endblock doc -%}
```
主要用到两个块: navbar(导航栏)和content(页面主要内容).

在templates文件夹下新建base.html文件

<small>templates/base.html</small>
```jinja2
{% extends 'bootstrap/base.html' %}

{% block title %}Just for fun{% endblock %}

{% block navbar %}
    <nav class="navbar navbar-inverse">
        <div class="container-fluid">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="/">Just for fun</a>
            </div>
            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                    <li><a href="/">Home</a></li>
                </ul>
            </div>
        </div>
    </nav>
{% endblock %}

{% block content %}
    <div class="container">
        {% block page_content %}{% endblock %}
    </div>
{% endblock %}
```

然后我们更改一下index.html和user.html
<small>templates/index.html</small>
```jinja2
{% extends 'base.html' %}

{% block page_content %}
    <div class="page-header">
        <h1>Hello World!</h1>
    </div>
{% endblock %}
```
<small>templates/user.html</small>
```jinja2
{% extends 'base.html' %}

{% block page_content %}
    <div class="page-header">
        <h1>Hello {{ name }}.</h1>
    </div>
{% endblock %}
```
OK,我们运行一下看看效果:
![](http://img.vim-cn.com/62/ad0e9a8cd76db05f4267f2dfebc4716bd86f0f.png)

还不错.

### 自定义错误页面.
有时候输入一个错误的网址的时候,会返回一个404 page not found错误.
分别在templates文件夹下创建404.html和500.html

<small>templates/404.html</small>
```jinja2
{% extends 'base.html' %}

{% block title %}404 - Page Not Found{% endblock %}

{% block page_content %}
    <div class="page-header">
        <h1>Not Found</h1>
    </div>
{% endblock %}
```
<small>templates/500.html</small>
```jinja2
{% extends 'base.html' %}

{% block title %}500 - Internal Server Error{% endblock %}

{% block page_content %}
    <div class="page-header">
        <h1>Server Error</h1>
    </div>
{% endblock %}
```
以及我们要在blog.py中添加相应的路由:

<small>blog.py</small>
```python
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
```

![](http://img.vim-cn.com/7d/184b4965124b019a1aa2b85f8445bd80c9f47d.png)

看一下blog.py的完整代码:
<small>blog.py</small>
```python
from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/')
def hello_world():
    return render_template('index.html')


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
    app.run(debug=True)
```
在最后一行,我加入了:debug=True,目的是当你对程序做出了改变之后,不需要手动重启项目,项目会自动帮你做出重启.

最后说一点内容,下一篇将会用到
## 使用Flask-Script支持命令行选项
安装Flask-Script:
```
pip install flask-script
```
Flask的开发web服务器支持很多启动设置选项,传递设置选项的理想方式是使用命令行参数.

e.g.:
```python
from flask_script import Manager
manager = Manager(app)

# ...

if __name__ == '__main__':
    manager.run()
```

此时的完整代码：
<small>blog.py</small>
```python
from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_script import Manager

app = Flask(__name__)
bootstrap = Bootstrap(app)
manager = Manager(app)


@app.route('/')
def hello_world():
    return render_template('index.html')


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
现在如何启动程序？

![](http://img.vim-cn.com/c9/878ea4942459a4a10af794eab4c8ff56a1e781.png)

在软件的左下角,选择点击Terminal,
输入:
```
python3 blog.py runserver
```

如下:

![](http://img.vim-cn.com/af/1873798f4d0fd05bb7b803e6a4d0732a13167d.png)

这里要注意一下,我目前使用的是我的Linux系统,Python2和Python3都有,所以这里写明是Python3,如果你电脑上只有Python3,那么你把这里的python3替换成python就可以了.按照自己电脑为主.

然后打开浏览器,在地址栏填入: http://localhost:5000/ 回车就可以了.
