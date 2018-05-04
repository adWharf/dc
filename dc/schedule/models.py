#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: models.py
@time: 04/05/2018 10:34
"""

from orator import Model, SoftDeletes
from orator.orm import has_many, belongs_to


class BaseModel(Model, SoftDeletes):
    __guarded__ = []


class Strategy(BaseModel):
    __table__ = 'trim_strategies'

    @has_many
    def filters(self):
        return Filter

    @has_many
    def history_filters(self):
        return HistoryFilter

    @has_many
    def trims(self):
        return Trim


class Filter(BaseModel):
    __table__ = 'trim_filters'

    @belongs_to
    def strategy(self):
        return Strategy


class HistoryFilter(BaseModel):
    __table__ = 'trim_history_filters'

    @belongs_to
    def strategy(self):
        return Strategy


class Trim(BaseModel):
    __table__ = 'trims'

    @belongs_to
    def strategy(self):
        return Strategy


class Action(BaseModel):
    __table__ = 'trim_actions'

    @belongs_to
    def strategy(self):
        return Strategy
