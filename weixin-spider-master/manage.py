# -*- encoding: utf-8 -*-
# !/usr/bin/python3
# @Time   : 2019/7/2 10:20
# @File   : manage.py
from settings import DEBUG
from webapp import app

if __name__ == '__main__':
    app.run(port=5000, debug=DEBUG)
