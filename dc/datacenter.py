#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: datacenter.py
@time: 10/04/2018 15:24
"""
from flask import Flask
import multiprocessing
from dc.catcher import Reporter, Commander

app = Flask(__name__)


class DC(object):
    def __init__(self):
        threads = [
            multiprocessing.Process(target=Reporter),
            multiprocessing.Process(target=Commander)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()


if __name__ == '__main__':
    dc = DC()

