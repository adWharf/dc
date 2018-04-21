#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: migration.py
@time: 10/04/2018 22:19
"""

from orator import Schema
from migrations import agency, account, point


def migrate(schema: Schema):
    '''
    Entrance of migrations
    :param schema:
    :return:
    '''
    account.migrate(schema)
    agency.migrate(schema)
    point.migrate(schema)


def rollback(schema: Schema):
    account.rollback(schema)
    agency.rollback(schema)
    point.rollback(schema)

