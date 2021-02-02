from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/hello')
def hello():
    return 'wscats'

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

# 确保服务器只会在该脚本被 Python 解释器直接执行的时候才会运行
if __name__ == '__main__':
    app.run()