from flask import render_template
from . import main
from ..models import Article


@main.route('/', methods=['GET', 'POST'])
def index():
    articles = Article.query.all()
    return render_template('index.html', articles=articles)


@main.route('/article/<title>')
def article(title):
    article = Article.query.filter_by(title=title).first()
    return render_template('article.html', title=title, content=article.content)
