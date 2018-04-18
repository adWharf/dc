#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: cli.py
@time: 10/04/2018 16:42
"""
import sys
import click
from core import config
from core.db import get_mysql_client
from orator import Schema


@click.group()
def cli():
    pass


@cli.command()
def migrate():
    from migration import migrate
    db = get_mysql_client(config.get('app.db.mysql'))
    schema = Schema(db)
    migrate(schema)


@cli.command('migrate:rollback')
def rollback():
    from migration import rollback
    db = get_mysql_client(config.get('app.db.mysql'))
    schema = Schema(db)
    rollback(schema)


if __name__ == '__main__':
    cli()

