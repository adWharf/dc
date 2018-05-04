#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: scheduler.py
@time: 03/05/2018 22:59
"""
from .bowler import HttpBowler, KafkaBowler
from .gardener import Gardener


class Scheduler(object):
    def __init__(self):
        bowler = KafkaBowler()
        self._gardener = Gardener(bowler)
        # self._gardener_pid = Process(target=self._gardener.trim)
        pass

    def run(self):
        self._gardener.trim()

    def __del__(self):
        pass
