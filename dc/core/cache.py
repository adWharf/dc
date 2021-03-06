#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: cache.py
@time: 03/03/2018 23:30
"""
from . import db, config


_enable = config.get('app.cache.enable')
_client = None
if _enable:
    _client = db.get_redis_client(config.get('app.redis'))


def _check_enable():
    if not _enable:
        raise Exception('Cache is disabled')


def put(key, value, ttl=None):
    _check_enable()
    _client.set(key, value, ttl)


def get(key):
    _check_enable()
    val = _client.get(key)
    if isinstance(val, bytes):
        val = bytes.decode(val)
    return val


def delete(key):
    _check_enable()
    return _client.delete(key)
