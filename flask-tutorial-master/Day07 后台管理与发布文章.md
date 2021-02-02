# 后台管理与发布文章

源代码: https://github.com/ltoddy/flask-tutorial

技术交流群:630398887(欢迎一起吹牛)

写在前面的话：如果你实在不会写页面,复制粘贴你会吧.

> https://getbootstrap.com/docs/3.3/examples/theme/

这个页面是,bootstrap样式表的例样,

> http://getbootstrap.com/docs/4.0/examples/

这个页面是,你进去看那个页面合适,你点进去,然后右键查看网页源代码,复制就好了,顺便说一下,别忘了把CSS也复制了.

我们来定义下我们的文章模型,文章内容放到数据库里面，然后通过查询文章标题来，在主页建立文章链接。

<small>app/models.py</small>

```python
class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    content = db.Column(db.Text)
```

文章模型很简单，一个id，一个文章标题，一个文章的内容这三个字段。
content = db.Column(db.Text),这里，回顾一下或者百度一下SQLAlchemy的列模型。

因为我们文章内容可不是几个字，而是很多上千上万字说不定，所以就不能再用简单的db.String来处理了。
我们使用db.Text这个，他对长文本做了优化.

当我们有了这个数据库的文章模型之后，为了给数据库添加数据，那么我们还需要相对应的表单：

<small>app/admin/forms.py</small>

```python
class PostForm(FlaskForm):
    title = StringField('文章标题:', validators=[Required()])
    content = TextAreaField('文章内容', validators=[Required()])
    submit = SubmitField('发布')
```

你看注意看变量的名字，我们最可能的让表单和文章模型中的变量去相同的名字，这样方便。

OK,继续。我们有了表单，要在页面中呈现出来。

<small>app/admin/views.py</small>

```python
from ..models import Article

@admin.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if not current_user.is_authenticated:
        return redirect(url_for('admin.login'))
    if form.validate_on_submit():
        try:
            article = Article(title=form.title.data, content=form.content.data)
            db.session.add(article)
            form.title.data = ''
            form.content.data = ''
            flash('发布成功')
        except:
            flash('文章标题有重复')
    return render_template('admin/index.html', form=form)
```

这段代码也没什么难度，先去创建一个表单form，然后判断一下你是否登录了，没登录的话就会重定向到登录界面。
继续往下，让你提交表单的时候，这里用到了一个try - catch语句，其实这里原因是，我最初想把那个数据库文章模型中title字段设置成unique的，title = db.Column(db.String(64),unique=True),后来想想算了，所不定有相同标题的文章呢。然后就是从表单中获取数据,来构件新的文章，然后存到数据库里面。
flash就是用来做一个提示，方便你自己知道你都干了啥事。

OK，把我们的HTML页面也说一下。

```jinja
{% extends 'admin/base.html' %}

{% import 'bootstrap/wtf.html' as wtf %}

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
                <ul class="nav navbar-nav navbar-right">
                    <li><a href="#" data-toggle="dropdown" class="dropdown-toggle">当前用户名为:{{ current_user.username }} <b
                            class="caret"></b></a>
                        <ul class="dropdown-menu">
                            <li><a href="{{ url_for('admin.logout') }}">退出当前账户</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
{%endblock%}

{% block page_content %}
    <div class="page-header">
        {{ wtf.quick_form(form) }}
    </div>
{%endblock%}
```

唯一做出了更改的地方就是 ```{% block page_content %}``` 这里，里面加入了一个表单.
OK,启动一下我们的项目看看效果。

![](http://img.vim-cn.com/49/56d76adbd7ec1f2eda090edfed2f05a93b489f.png)

当然你可能会出现一个SQLAlchemy的异常，如何解决：

```
$ python3 manage.py shell
>>> from manage import *
>>> db.drop_all()
>>> db.create_all()
>>> exit()
```

更新一下我们的数据库结构，毕竟我们更改了数据库模型，添加了文章这个模型。
注意哦，每当我们更改了app/models.py这个文件,我们最好都要重新设置一下数据库.

我们现在已经可以把文章放到数据库了，现在我们要把数据库的文章显示出来。
在这里，我修改了一下templates/base.html页面:

```jinja
{% extends 'bootstrap/base.html' %}

{% block title %}Just for fun{% endblock %}

{% block navbar %}
    <nav class="navbar navbar-inverse" id="top">
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
{%endblock%}

{% block content %}
    {% for message in get_flashed_messages() %}
        <div class="alert alert-info">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            {{ message }}
        </div>
    {% endfor %}
    <div class="container">
        <div class="col-sm-8">
            {% block page_content %}{% endblock %}
        </div>
        <div class="col-sm-3 col-sm-offset-1">
            {% block slider %}{% endblock %}
        </div>
    </div>
{%endblock%}
```

只更改了最后，我把<div class="container">，切成了两个块，第一个块来放文章的内容，第二个块来放文章目录。

改完templates/base.html，我们在改一下templates/index.html，这是我们的主页，总显示一句话不好看，所以我们改一改。

```jinja
{% extends 'base.html' %}

{% import 'bootstrap/wtf.html' as wtf %}

{% block page_content %}
    <h1>欢迎来到我的blog</h1>
    <p>技术交流群：630398887</p>
    <hr>
    <div class="row">
        <h2>如下内容凑的字数</h2>
        <hr>
        <h3>登鹳雀楼</h3>
        <p>白日依山尽，黄河入海流。</p>
        <p>欲穷千里目，更上一层楼。</p>
        <hr>
        <h2>论语</h2>
        <p>子谓公冶长：“可妻也，虽在缧绁之中，非其罪也！”以其子妻之。</p>
        <p>子谓南容：“邦有道不废；邦无道免于刑戮。”以其兄之子妻之。</p>
        <p>子谓子贱：“君子哉若人！鲁无君子者，斯焉取斯？”</p>
        <p>子贡问曰：“赐也何如？”子曰：“女器也。”曰：“何器也？”曰：“瑚琏也。”</p>
        <p>或曰：“雍也仁而不佞。”子曰：“焉用佞？御人以口给，屡憎于人。不知其仁，焉用佞？”</p>
        <p>子使漆雕开仕，对曰：“吾斯之未能信。”子说。</p>
        <p>子曰：“道不行，乘桴浮于海，从我者其由与？”子路闻之喜，子曰：“由也好勇过我，无所取材。”</p>
        <p>
            孟武伯问：“子路仁乎？”子曰：“不知也。”又问，子曰：“由也，千乘之国，可使治其赋也，不知其仁也。”“求也何如？”子曰：“求也，千室之邑、百乘之家，可使为之宰也，不知其仁也。”“赤也何如？”子曰：“赤也，束带立于朝，可使与宾客言也，不知其仁也。”</p>
        <p>子谓子贡曰：“女与回也孰愈？”对曰：“赐也何敢望回？回也闻一以知十，赐也闻一以知二。”子曰：“弗如也，吾与女弗如也！”</p>
        <p> 宰予昼寝，子曰：“朽木不可雕也，粪土之墙不可杇也，于予与何诛？”子曰：“始吾于人也，听其言而信其行；今吾于人也，听其言而观其行。于予与改是。”</p>
        <p> 子曰：“吾未见刚者。”或对曰：“申枨。”子曰：“枨也欲，焉得刚。”</p>
        <p> 子贡曰：“我不欲人之加诸我也，吾亦欲无加诸人。”子曰：“赐也，非尔所及也。”</p>
        <p> 子贡曰：“夫子之文章，可得而闻也；夫子之言性与天道，不可得而闻也。”</p>
        <p> 子路有闻，未之能行，唯恐有闻。</p>
        <p> 子贡问曰：“孔文子何以谓之文也？”子曰：“敏而好学，不耻下问，是以谓之文也。”</p>
        <p> 子谓子产：“有君子之道四焉：其行己也恭，其事上也敬，其养民也惠，其使民也义。”</p>
        <p> 子曰：“晏平仲善与人交，久而敬之。”</p>
        <p>
            子张问曰：“令尹子文三仕为令尹，无喜色，三已之无愠色，旧令尹之政必以告新令尹，何如？”子曰：“忠矣。”曰：“仁矣乎？”曰：“未知，焉得仁？”“崔子弑齐君，陈文子有马十乘，弃而违之。至于他邦，则曰：‘犹吾大夫崔子也。’违之。之一邦，则又曰：‘犹吾大夫崔子也。’违之，何如？”子曰：“清矣。”曰：“仁矣乎？”曰：“未知，焉得仁？”</p>
    </div>
{%endblock%}

{% block slider %}
    <ol class="list-unstyled">
        <li><h2>文章列表</h2></li>
        {% for article in articles %}
            <li><a href="article/{{ article.title }}">{{ article.title }}</a></li>
        {% endfor %}
    </ol>
{%endblock%}
```

当然，大部分内容去百度复制粘贴的，不过这里你要看一下这一段代码。

```jinja
{% block slider %}
    <ol class="list-unstyled">
        <li><h2>文章列表</h2></li>
        {% for article in articles %}
            <li><a href="article/{{ article.title }}">{{ article.title }}</a></li>
        {% endfor %}
    </ol>
{%endblock%}
```

我们利用一个for循环，通过视图函数传过来的参数，做了一个文章列表，效果如下：

![](http://img.vim-cn.com/3f/956db608a240c111a49a55123859936109a735.png)

为了把效果实现出来，我们需要在视图函数中把参数传进来，然后让Jinja2引擎渲染一下。
还记得之前提到Jinja2引擎的时候，它可以想在python里面一样可以解析复杂的数据类型，比如咱这个article。

```python
from ..models import Article


@main.route('/', methods=['GET', 'POST'])
def index():
    articles = Article.query.all()
    return render_template('index.html', articles=articles)
```

也很简单拉，把所有文章从数据库获取一下，传进去就好了。

能显示文章列表了，我们需要单独把文章显示出来。

```jinja
<li><a href="admin/article/{{ article.title }}">{{ article.title }}</a></li>
```

其实阿，这段代码，是我已经把代码都写好了的，因为这个时候你可能还没有把相关的html页面写好。所以说那个a标签中的href属性可以先不写，然后等会在写就好。

<small>app/templates/article.html</small>

```jinja
{% extends 'base.html' %}

{% block page_content %}
    <div class="page-header"><h1>{{ title }}</h1></div>
    <div class="well">{{ content }}</div>
{%endblock%}
```

文章的页面也很简单，一个标题，一个内容。两个变量。

再看一下视图函数:

```python
@main.route('/article/<title>')
def article(title):
    article = Article.query.filter_by(title=title).first()
    return render_template('article.html', title=title, content=article.content)
```

你看这里，还记得动态路由么，这里用到了动态路由，通过文章的标题来从数据库把这篇文章数据获取出来。
然后把标题和文章内容传参到HTML页面就可以了。

这个时候，你就可以把app/templates/index.html页面中那个文章列表的a标签的href属性补全了。

这里说一下，你看啊，我们的功能在不断的增加，可是基本上都没有大幅度改动我们的原先的代码，而是为新功能写好代码，添加进去。这是一个非常好的表现，增加新功能而又不与原先代码有冲突。
