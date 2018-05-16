#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: datacenter.py
@time: 10/04/2018 15:24
"""
import multiprocessing
from dc.catcher import Reporter, Commander


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

