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
from migrations import account, agency, point, user


def migrate(schema: Schema):
    '''
    Entrance of migrations
    :param schema:
    :return:
    '''
    account.migrate(schema)
    agency.migrate(schema)
    point.migrate(schema)
    user.migrate(schema)
    # for p, d, files in os.walk(os.path.join(config.APP_PATH, 'migrations')):
    #     for f in files:
    #         name = f.split('.')[0]
    #         if not name.startswith('__'):
    #             pck = importlib.import_module('.migrations.' + name, name)
    #             print(pck)
    #             getattr(getattr(migrations, name), 'migrate')(schema)


def rollback(schema: Schema):
    account.rollback(schema)
    agency.rollback(schema)
    point.rollback(schema)
    user.rollback(schema)
    pass
