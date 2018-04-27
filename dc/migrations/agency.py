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
    if schema.has_table('agencies'):
        return
    with schema.create('agencies') as table:
        table.big_increments('id')
        table.string('name')
        table.string('display_name')
        table.timestamps()
        table.unique('name')

    schema.db.table('agencies').insert([
        {'name': 'wxext', 'display_name': '微信插件'}
    ])


def rollback(schema: Schema):
    schema.drop('agencies')
