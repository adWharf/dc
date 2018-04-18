#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: catcher.py
@time: 12/04/2018 18:32
"""
from core import db, config
import influxdb


class Catcher(object):

    def __init__(self):
        self._db = db.get_mysql_client(config.get('app.db.mysql'))
        cfg = config.get('app.db.influxdb')
        self._influxdb = influxdb.InfluxDBClient(host=cfg['host'],
                                                 port=cfg['port'],
                                                 username=cfg['user'],
                                                 password=cfg['password'],
                                                 database=cfg['database'])