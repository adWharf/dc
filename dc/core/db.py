#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: william wei 
@license: Apache Licence  
@contact: weixiaole@baidu.com
@file: db.py 
@time: 19/01/2018 2:31 PM 
"""

from orator import DatabaseManager
from pymongo import MongoClient
import redis
import etcd

# TODO Reuse connections
__clients = {}


def get_mysql_client(config):
    return DatabaseManager({
        'default': 'mysql',
        'mysql': config
    })


def get_mongo_client(config):
    '''
    Doc: http://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection
    :param config:
    :return:
    '''
    for key in ['user', 'password', 'host', 'port']:
        if key not in config:
            config[key] = None
    if "database" not in config:
        raise Exception('database is necessary when connecting mongodb')
    if 'auth_database' not in config:
        config['auth_database'] = config['database']

    conn = MongoClient(username=config['user'],
                       password=config['password'],
                       host=config['host'],
                       port=config['port'],
                       authSource=config['auth_database'])
    return conn[config['database']]


def get_redis_client(config):
    return redis.Redis(host=config['host'],
                       port=config['port'],
                       db=config['db'])


def get_etcd_client(config):
    return etcd.Client(host=config['host'], port=config['port'])
