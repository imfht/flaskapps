# 使用Flask-Mail提供电子邮件支持

使用pip安装Flask-Mail
```
pip install flask-mail
```

这里使用163的邮箱作为发送者。
注册163邮箱之后，去设置 -> POP3/SMTP/IMAP(在右侧导航栏)，然后开启你的SMTP服务，这时候会让你设置客户端授权码，这个授权码是重点，一定要记住。


类型|服务器名称|服务器地址|SSL协议端口号|非SSL协议端口号
----|---|---|---|---
发件服务器|SMTP |smtp.163.com|465/994|25|

把这个表格也关注一下，里面的内容要去写到配置中去。

源码:
```python
from flask import Flask
from flask.ext.mail import Mail, Message

app = Flask(__name__)
# 下面是SMTP服务器配置
app.config['MAIL_SERVER'] = 'smtp.163.com'  # 电子邮件服务器的主机名或IP地址
app.config['MAIL_PORT'] = 25  # 电子邮件服务器的端口
app.config['MAIL_USE_TLS'] = True  # 启用传输层安全
# 注意这里启用的是TLS协议(transport layer security)，而不是SSL协议所以用的是25号端口
app.config['MAIL_USERNAME'] = 'username@163.com'  # 你的邮件账户用户名
app.config['MAIL_PASSWORD'] = 'password'  # 邮件账户的密码,这个密码是指的授权码!授权码!授权码!

mail = Mail(app)


@app.route('/')
def index():
    msg = Message('你好', sender='username@163.com', recipients=['you@example.com'])
    # 这里的sender是发信人，写上你发信人的名字，比如张三。
    # recipients是收信人，用一个列表去表示。
    msg.body = '你好'
    msg.html = '<b>你好</b> stranger'
    mail.send(msg)
    return '<h1>邮件发送成功</h1>'


if __name__ == '__main__':
    app.run(debug=True)
```

值得注意的一点是，如果你是刚刚创建的163的邮箱，你最好先用163邮箱发送一封邮件，因为你在发送第一封邮件的时候，会让你设置发件人名字，如果不设置的话，你的邮件会被退回。
