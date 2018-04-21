#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: account.py
@time: 21/04/2018 18:26
"""
from orator import Schema


def migrate(schema: Schema):
    with schema.create('accounts') as table:
        table.big_increments('id')
        table.string('agency')
        table.string('username').nullable()
        table.string('password').nullable()
        table.string('phone').nullable()
        table.string('access_key').nullable()
        table.string('secret_key').nullable()
        table.timestamps()


def rollback(schema: Schema):
    schema.drop('accounts')
