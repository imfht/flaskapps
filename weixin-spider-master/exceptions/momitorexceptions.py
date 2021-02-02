# -*- coding: utf-8 -*-
# @Time    : 2019/8/10 10:03
# @Author  : xzkzdx
# @File    : momitorexceptions.py


class NoneKeyUinError(ValueError):
    def __init__(self, *args):
        super(NoneKeyUinError, self).__init__(*args)


if __name__ == "__main__":
    pass
