#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: user.py
@time: 21/04/2018 21:52
"""
from orator import Schema


def migrate(schema: Schema):
    with schema.create('users') as table:
        table.big_increments('id')
        table.string('name')
        table.string('username')
        table.string('password')
        table.timestamps()


def rollback(schema: Schema):
    schema.drop('users')
