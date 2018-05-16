#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: bowler.py
@time: 03/05/2018 15:38
"""
import time
import json
from multiprocessing import Process, Pipe
from .httpbridge import run as build_bridge
from kafka import KafkaConsumer
from dc.constants.topics import AD_PROCESSED_TOPIC
from dc.core import config, logger, db


logger = logger.get('Schedule.Bowler')


class Bowler(object):
    def __init__(self):
        self._db = db.get_mysql_client(config.get('app.db.mysql'))
        self._iterator = None

    def __iter__(self):
        return self

    def __next__(self):
        '''
        Produce data
        :return:
        '''
        if not self._iterator:
            self._iterator = self._msg_generator()
        try:
            return next(self._iterator)
        except StopIteration:
            self._iterator = None
            raise

    def _msg_generator(self):
        raise NotImplemented


class KafkaBowler(Bowler):
    def __init__(self):
        Bowler.__init__(self)
        kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
        self._consumer = KafkaConsumer(AD_PROCESSED_TOPIC,
                                       client_id='ad_statistic_catcher_reporter',
                                       group_id='ad_statistic_catcher',
                                       bootstrap_servers=kafka_server)
        logger.info('Connect to kafka[%s] successfully' % kafka_server)

    def _msg_generator(self):
        for msg in self._consumer:
            try:
                data = json.loads(msg.value)
                yield data
            except Exception as e:
                logger.error(e)


class HttpBowler(Bowler):
    def __init__(self):
        Bowler.__init__(self)
        self._data_q, another_data_end = Pipe()
        self._command_q, another_command_end = Pipe()
        self._bridge = Process(target=build_bridge, args=(another_data_end, another_command_end))
        self._bridge.start()

    def _msg_generator(self):
        while True:
            while self._data_q.poll():
                try:
                    logger.info('Receive ad data')
                    data = str(self._data_q.recv_bytes(), encoding='utf-8')
                    yield json.loads(data)
                except Exception as e:
                    logger.error(e)
            time.sleep(5)

