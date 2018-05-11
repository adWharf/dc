#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: commander.py
@time: 04/05/2018 11:38
"""
import json
from kafka import KafkaProducer
from dc.core import config, logger
from dc.constants.topics import AGENCY_COMMAND_TOPIC

logger = logger.get('Schedule.Commander')


class Commander(object):
    def __init__(self):
        pass

    def transmit(self, actions):
        raise NotImplemented


class KafkaTopicCommander(Commander):
    def __init__(self):
        Commander.__init__(self)
        kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
        self._producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                       client_id='agency_commander',
                                       compression_type='gzip',
                                       bootstrap_servers=kafka_server,
                                       retries=3)

    def transmit(self, actions):
        self._producer.send(AGENCY_COMMAND_TOPIC, actions)
        return False


class HttpCommander(Commander):
    def __init__(self):
        Commander.__init__(self)

