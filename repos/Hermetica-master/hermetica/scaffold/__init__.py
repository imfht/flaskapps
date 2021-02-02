#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
__init__.py
Scaffold Abstract
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '1.0.0'
__date__ = '2018-04-27'


class Scaffold(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def write(self, source_code):
        with open(self.filepath, 'w') as py:
            py.write(source_code)
