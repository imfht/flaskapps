# Hello Flask

源代码: https://github.com/ltoddy/flask-tutorial

技术交流群:630398887(欢迎一起吹牛)

写在前面的话：这里我假设你电脑已经安装好了Python3，本项目基于Python3开发。(没有pip没关系)

### 什么是pip？
pip就是一个软件包管理，因为有各种人士开发了python的第三方库，但是这些库是不在标准库中的，这些库发布在PyPi上。所以可以使用pip这个工具来自动下载。


## 环境搭建:
所选用的集成开发环境(也就是开发软件)是：Pycharm Professional

去jetbrains官网 [click me](https://www.jetbrains.com/)
![Pycharm](https://img.vim-cn.com/33/da78b993e3f26d1a6f88f83810fa40048000f9.png)

![Pycharm Professional](https://img.vim-cn.com/ea/cf73e1115185cddd5457ccc1d3d52683579e5c.png)

有两个版本一个是Professional(专业版)，一个是Community(社区版)。
这里我们下载Professional版。

顺便提一句，这个软件内部已经集成好了pip，所以你不需要自己手动去安装pip。


然后下载好Pycharm Professional之后，去安装，没什么问题就下一步就好。

![](https://img.vim-cn.com/1c/a0d7cdff71fed5e8c1ac3f0299c5376d0898f4.png)

如果你是第一次下载使用，点击Do not import settings,这里的意思就是说，如果你之前用过这个软件，本地是由相关的配置文件的，比如保存着软件的主题，插件之类的东西。

![](https://img.vim-cn.com/0e/59840c75f7b97cf8d81338344e8b53bc174656.png)

因为这是个付费软件，但是可以免费使用三十天。说句公道话，不要埋怨什么软件付费，你想想，公司人员花了力气开发出来东西，凭什么就让你白白使用。换做是谁都不愿意啊。

然后点击 Evaluate， 然后点击Accept。

![](https://img.vim-cn.com/4b/e6e1c874e626956cc9d248705a08eec99eb345.png)
这里是让你去选择你软件的快捷键，主题，字体，颜色。选好之后点OK就好。

然后点击create new project

![](https://img.vim-cn.com/e7/6363711a0254f8dc350151ebf04a6a4afc45bc.png)

这里我们项目取名字为blog。(仅仅是把上面的Location中最后untitled改成了blog)。
然后点击create。

然后等一小会，软件把Python3的标准库和第三方库导入进去。

![](https://img.vim-cn.com/28/8ea1f7973af837e5a2b34790ce8937b5acd8b3.png)

进去之后是如上图的样子。

![](https://img.vim-cn.com/0e/8f793910536cb1f49cd6d25983ec219bfb2ffe.png)

如果你电脑没有相关的第三方库(这里指的flask库，和相关的扩展库)的话，把鼠标一到有红色下划线的地方，然后会有一个橙红色的灯泡，点击一下，然后点击第一个选项(Install package flask),让软件自身集成的pip给你安装好。
然后等一小会，就安装好了，然后你就会看到红色下划线消失了。

然后我们鼠标右键，然后点击运行。
![](https://img.vim-cn.com/df/8a134d2a4365317c3fe4a992a876e5d8673b6a.png)

下方出现如下效果，然后点击那个网址。

![](https://img.vim-cn.com/80/d1f54859f1bd6964d9dd74faa6fa4ce4ba9479.png)

![](https://img.vim-cn.com/b2/7fc128c89b4ca956f4039557d6717b501fc5d6.png)

他会自动打开电脑默认的浏览器去浏览。

#### 这里写给外行，非计算机人士
![](https://img.vim-cn.com/80/d1f54859f1bd6964d9dd74faa6fa4ce4ba9479.png)
这在里的最左侧，有这么几个功能按钮，Rerun(重新启动这个程序),Stop(停止这个程序)。让你不浏览程序的结果的时候，尽量就Stop这个程序。因为这个程序会占用电脑的5000端口号，然后每次运行就会占用这个端口号，当你程序已经运行之后，再更新了代码看效果的时候，如果你还想再去run这个程序，那么会提示你有Rerun那个选项，
![](https://img.vim-cn.com/65/93f7908015842775faebef47280edfd8fed4bd.png) 点击那个Stop and Rerun就好。不过这样子总感觉怪怪的。


再次回归正题。

## 感受一下动态路由。
代码如下:

blog/blog.py
```python
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/<username>')
def user(username):
    return "Hello {}".format(username)


if __name__ == '__main__':
    app.run()
```
然后手动的去更改一下网址，如下。看上去还不错。
![](https://img.vim-cn.com/1d/f36c666f2ff2aed05739897d024c45a31dcf65.png)

## OK，下面讲解一下Flask框架。

Flask主要有两个依赖:路由，Web服务器网关接口子系统(由Werkzeug提供)；和模板系统(由Jinja2提供，下一节将会用到)。

简单说一下路由:

```python
app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World!'
```
简单说一下这个部分代码，app = Flask(\_\_name\_\_)，用来创建一个Flask应用，一般Flask类构造函数只有一个必须指定的参数，即程序主模块或包的名字，在大多数程序中，Python的__name___变量就是所需要的值。
@app.route('/') 这个东西叫路由，程序实例需要知道对每个URL(网址)请求运用那些代码，所以保存了一个URL到Python函数的映射关系。处理URL和函数之间的关系的程序称为路由。而下面所修饰的index()函数被叫做视图函数，他来展示你的web页面的样子。


最后说一点，我是linux用户，之后的讲解我就在我的ubuntu上写了，如果windows上和linux上有区别的地方，我会以windows为主，毕竟我有两台电脑。
