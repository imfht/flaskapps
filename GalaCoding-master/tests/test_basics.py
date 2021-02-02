# -*- coding:utf8 -*-
'''
Basic test py file.
'''
import unittest
from flask import current_app
from app import create_app, db

'''
    这个测试使用 Python 标准库中的 unittest 包编写。 setUp() 和 tearDown() 方法分别在各
测试前后运行，并且名字以 test_ 开头的函数都作为测试执行。
    setUp() 方法尝试创建一个测试环境，类似于运行中的程序。首先，使用测试配置创建程
序，然后激活上下文。 这一步的作用是确保能在测试中使用 current_app，像普通请求一
样。然后创建一个全新的数据库， 以备不时之需。数据库和程序上下文在 tearDown() 方法
中删除。
    所有以test_xxx开头的函数在测试时，自动运行，并显示结果。
    第一个测试确保程序实例存在。 第二个测试确保程序在测试配置中运行。若想把 tests 文
件夹作为包使用， 需要添加 tests/__init__.py 文件，不过这个文件可以为空，因为 unittest
包会扫描所有模块并查找测试。
'''
class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])