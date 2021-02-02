# 基于Flask的博客系统搭建

最近在学习python，然后呢，python的用处还很多，原来计划搞机器学习和数据挖掘的，不幸.....看到python可以开发后端，一时技痒，就学习了，当时从网上找了很多资料，还有就是当时要参加比赛，所以肯定是越快上手越好，越小越好，后来选择了flask，现在静下心来看《FlaskWeb开发：基于Python的Web应用开发实战》一书，然后随着书本逐步学习flask并且逐步完善本博客系统。[GalaCoding](https://github.com/GalaIO/GalaCoding)现在开源，并托管在github上。希望大家可以多多交流~~
#### 与Flasky的区别
在《FlaskWeb开发：基于Python的Web应用开发实战》一书中，实现的简单博客功能，包括用户认证、登录、注册系统，博客编写页面，评论功能，用户资料主页，用户关注等功能。

我在学习的基础上增加了一些功能：
- 博客关注功能，新增了推荐和关注页面，也就是说，广场的形式就是推送目前较新的博客，推荐是推荐关注的博主的最新博文，关注是关心的博客的动态；
- 添加了态度评论，即可以给博客和评论进行点赞，表示赞同和不赞同；- - 添加了云标签，可以通过热门标签来获得网站的动态。

修改的功能：
- 对网站进行了改版，页面的更换，样式的修改；
- 对于用户头像，采用离线缓存**Gravatar**的两种类型头像，然后使用邮箱地址的一个映射函数，让用户获取默认头像；
- 修改了posts表的模型，去掉html_body属性，也就是说服务端不缓存Markdown的html版本，在浏览器端使用[marked]()来形成实时编辑和预览，以及渲染的工作；

后期新增功能：
- 添加评论的评论功能，实现盖楼评论；
- 修改博客编辑页面，使其更友好，支持更多的markdown的类型；
- 增加图片墙的功能，让用户可以上传图片；
- 支持markdown文档上传，生成博客的功能。




#### 一、启动
###### 1.安装环境

如果使用这个模板很简单，首先你需要下载源码（这是当然的），然后安装python2.7环境，对于linux用户，python2.7是标配的，windows需要根据版本下载python安装程序就好了。下面给出ubuntu下的python安装。

```bash
$sudo apt-get install -y python python-pip
```
然后需要安装依赖库，你也可以在虚拟环境中安装哦，这样更方便一点。
```bash
$sudo pip install -r requirements.txt
```
所有与环境相关的配置，都在**config.py**文件中，不过你不用修改它，因为这些配置信息都来自于系统的环境变量，你可以设置环境变量来大概修改配置的目的，同时满足了隐私。值得一提是，我们提供了一个脚本来自动的初始化配置信息和加载必要的环境变量，为了保护隐私，我给注释了但是使用者必须填写，具体操作在第八节，我先说明一下需要配置的环境变量。
```bash
# 加密密钥
#export SECRET_KE=
# 服务器绑定二级域名 端口 和过滤IP地址设置
#export WEBSERVER_HOST=
#export WEBSERVER_PORT=
export WEBSERVER_ACCESSIP=127.0.0.1
# 注册发送邮件服务器
#export MAIL_SERVE=
#export MAIL_SERVERPORT=
#export MAIL_USERNAME=
#export MAIL_PASSWORD=
#export MAIL_ADDR=
# Database地址
#export DEV_DATABASE_URL=
#export TEST_DATABASE_URL=
#export DATABASE_URL=
```
设置好后，可以直接运行**run.sh**进行测试（第八节），当然你也可以手动的把环境变量输入（这是必须的），然后直接运行manage.py脚本进行测试。
>最好的一个选择是，配置好run.sh下的环境变量，使用sudo执行，然后再进行下列命令，因为这时候系统已经保存有这些环境变量了。也可以把他们放在自己的bash.rc配置文件中。

###### 2.数据库迁移
使用flask-migrate后，数据库迁移变得so easy，同时本步骤是必须的，有可能你下载下来的**master**版本是已经生成数据库了，默认的是SQLLite，但是你可以把miratation文件夹和sqllite文件删除，来重新迁移数据库，也就是重新建表。

迁移工程初始化，该步骤可以初始化一个迁移工程为后续做准备。
```bash
$python manage.py db init
```
初始化后，需要实行migrate指令，来生成迁移脚本，也就是说迁移工具自动生成配置数据库的脚本，该步骤必须显示调用。
```bash
$python manage.py db migrate -m "init version"
```
生成迁移脚本了，那么就开始正式迁移了，运行下面命令即可，如果没有数据库表，该命令会显式创建，同时运行迁移脚本，迁移数据库。
```bash
$python manage.py db upgrade
```
好了，现在数据库迁移完成了，可以进行下一步了。
###### 3.启动前准备
现在虽说基本建好环境了，但是对了本博客系统实现了简单的权限管理，所以必须显式的建立权限角色，否则会出现绑定角色失败，用户只能沦为无权限状态。不过新建角色也很简单。
```bash
$python manage.py shell

>>> Role.insert_roles()
>>> Role.query.all()
[<Role u'Moderator'>, <Role u'Administrator'>, <Role u'User'>]
>>>
```
还有就是建立一个初始的超级管理员，步骤如下：
```bash
$python manage.py shell

>>> u = User(username='GalaIO', email='*****@**.com', role=Role.query.filter_by(name='Administrator').first(), password='***')
>>> u.generate_avatar_url()
>>> u
<User 'GalaIO'>
>>> db.session.add(u)
>>> db.session.commit()
```
现在你只需要完成邮件验证就好了，当然这个你也可以通过后台数据库操作。
还有为了支持匿名评论功能，需要主动的添加一个匿名用户，如果没有设置，系统会报异常来提示的。操作也很简单。
```bash
$python manage.py shell

>>> User.insert_Anonymous()
```
这时就可以匿名评论了，实现匿名功能随后细聊，匿名用户比较特殊，只可以评论，同时也只有名字属性，其他属性为None。
###### 4.运行
flask-script支持以下面命令启动应用。
```bash
$python manage.py runserver
```

这时候就可以完美访问你的服务器了，但是需要注意的是这时只能本机访问，如果需要外部计算机访问，可以添加参数，指定所有IP可访问，即0.0.0.0，同时可指定绑定的端口号。

```bash

$python manage.py runserver -h 0.0.0.0 -p 8000

 * Restarting with stat

 * Debugger is active!

 * Debugger pin code: 113-835-817

 * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)

```

如果需要更多功能选项，可以访问如下命令来查看。

```bash

$python manage.py runserver --help

```
值得一提是，本博客实现了一个默认命令，也就是说直接执行：
```bash
$python manage.py
```
也可以运行服务器，而端口和可访问的ip段在**Config**类中定义，可以修改。

#### 二、在shell环境中使用flask和数据库

这个比较简单，在键入命令后，在后台模板会自动把app实例、sqlalchemy实例、数据库定义自动的加载到shell中，你可以在其中自由做测试，或者手动添加、修改数据库等。博客建立的所有模型，在这个交互环境中都有映射。

```bash

$python manage.py shell

>>> app

<Flask 'app'>

>>> db

<SQLAlchemy engine='sqlite:///C:\\Users\\GalaIO\\Desktop\\GalaIO\\flask_pro\\data-dev.sqlite'>

>>> System

<class 'app.models.System'>

>>>

```

#### 三、使用数据库迁移工具

数据库迁移已经建立了一个基本版本，如果需要更新数据库模型，如果移动到新的部署环境，可以直接运行下面命令来同步数据库。也就是说如果初次建立后，如果更新了数据库模型，那么你可以使用如下命令来更新数据库，一个是生成迁移脚本，一个执行升级功能，但是需要注意新增表和属性好办，如果删除了现有的表和属性，那么你得手动处理migrate命令生成的脚本是否正确。

```bash
$python manage.py db migrate
$python manage.py db upgrade
```

#### 四、修改配置文件

该结构框架提供了灵活的修改模式，如果添加一些配置项，可以添加在**Config**类中，如果想在生产环境和开发、测试环境使用不同的参数，需要在扩展类中进行修改，不过最通用的参数使用系统的环境变量。



这时一个从环境变量中引用密钥的例子，**or**的作用是在环境变量不起作用时，拥有替代方案。

```python

import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess'

```

在配置文件可以同代项**app.config**字典中添加键值对，满足flask扩展库和全局通用量的需要，这些代码应写在如下：

```python

    @staticmethod

    def init_app(app):

		# you should write here

        pass

```

也就是说，我们的**SECRET_KEY**和**DATABASE_URL**默认从环境变量中引用，否则就使用默认字符串，或者在本地目录新建、寻找数据库。


同时我们还在Config中添加了，如下几个字段，由于配置生产环境时候，具体配置看8节。
```python
    HOST = 'blog.liketobe.cn'
    PORT = 8080
    ACCESSIPS = '127.0.0.1'
```

#### 五、增加模型

数据模型文件存在app目录下，添加数据模型很简单，只需要按照按照例子添加一个类就可以了，后台会自动完成，同时若想学习更多的**SQLalchemy**的**ORM**操作，可以访问<a href="http://www.sqlalchemy.org/support.html">SQLAlchemy官网</a>来获取资源。

```python

# test model

@addModel

class System(db.Model):

    name = db.Column(db.String(64), primary_key=True)

    def __repr__(self):

        return '<System %r>' % self.name

```

#### 六、模板与静态文件

**flask**会自动分发和处理对于**static**下的静态文件，一般包括**css**样式、**js**脚本、**img**图片等等。



**templates**目录下是所有的模板文件，由程序控制渲染展示给用户，这些都是flask的基础知识，这里不阐述，需要说明的是，我们提供了一个默认的根目录的模板**index.html**，还有常见错误类型**404.html**、**500.html**。如果想换成自己的样式，必须进行替换和更改，同时不影响你的其他创作。

#### 七、添加新的路由映射

模板提供了一个**index**路由的例子，可以先复制直接修改使用。值得提醒的是，可以把**errors**文件夹删除，因为他们定义的是全局的错误路由处理，主要修改的是**views.py**脚本，如果需要增加新的类声明的，在该文件夹下进行，最后当然需要在**__init__.py**中修改蓝图的名字，记得与包文件名一致，这些都是好的编码习惯哦。

#### 八、自动生成配置文件
使用python直接负责后台可能会有弊端，一般构造一个生产环境，现在是一个比较简单的，它会生成nginx和uwsgi的配置文件，这都是自动的，然后分别把配置文件放到相应的目录即可。更重要的是在其中会执行pip的依赖库备份，还有自动迁移和更新数据库。
```python
    # 利用bash命令删除所有的xml 和 conf文件，这些就是nginx和uwsgi的配置文件
    os.system('rm *-nginx.conf')
    os.system('rm *-uwsgi.xml')
    # 执行数据迁移和更新
    os.system('python manage.py db migrate')
    os.system('python manage.py db upgrade')
    # 执行角色更新
    Role.insert_roles()
    # 自动更新需求库
    os.system('pip freeze > requirements.txt')
```
命令执行如下：
```bash
$python manage.py conf
```
执行上述命令就会发现在本地目录出现一个****-nginx.conf和****-uswgi.xml两个文件，现在你需要电脑安装好这两个程序，一个是反向代理服务器nginx，另一个是python的通用网关接口uwsgi。安装命令如下：
```bash
$sudo apt-get install nginx
$sudo apt-get install uwsgi
```
把****-nginx.conf移动到nginx的配置文件，并且重新加载nginx的配置。
```bash
$sudo cp ./****-nginx.conf /etc/nginx/con.f/
$sudo /usr/sbin/nginx -s reload
```
启动uwsgi服务器，并手动设置log文件。
```bash
$sudo uwsgi -x ****-uwsgi.xml -d ./****.log
```
这样就简单搭建了生产环境。
>值得一提：我们提供了run.sh和exit.sh的脚本，用于自动运行和退出。如果有必须，可以使用chmod命令来给run.sh、exit.sh添加执行权限。
>

##### 九、添加新的库

在开发中往往需要添加新的库，但是需要说明的一点，希望大家进入虚拟环境中，使用pip安装，安装环境也打包了，当然这是windows上的虚拟环境，因为在虚拟环境安装会默认安装到**venv/Lib/site-packages/**中，我们程序每次动态吧改路径链入我们的库搜索路径，所以可以直接运行，就像步骤一说的一样。



如果安装了新的库，记得更新一下依赖库列表哦。运行如下命令。

```bash

$pip freeze > requirements.txt

```
