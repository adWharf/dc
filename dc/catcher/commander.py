#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: commander.py
@time: 16/05/2018 15:57
"""
import json
from .catcher import Catcher
from dc.core import config, logger
from kafka import KafkaConsumer
from dc.constants.topics import AGENCY_COMMAND_REPORTER_TOPIC
from dc.models import Action

logger = logger.get('Catcher.Commander')


class Commander(Catcher):
    def __init__(self):
        Catcher.__init__(self)
        kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
        logger.info('Try to connect to kafka...')
        self._consumer = KafkaConsumer(AGENCY_COMMAND_REPORTER_TOPIC,
                                       client_id='commander_result_reporter',
                                       group_id='commander_result_reporter',
                                       bootstrap_servers=kafka_server)
        logger.info('Connect to kafka[%s] successfully' % AGENCY_COMMAND_REPORTER_TOPIC)
        self._consumer_command_res()

    def _consumer_command_res(self):
        for msg in self._consumer:
            try:
                logger.info('Receive command results from kafka')
                action = json.loads(msg.value)
                Action.where('id', action['id']).update({
                    'resp_cnt': action['resp_cnt'],
                    'resp_status_code': action['resp_status']
                })
            except Exception as e:
                logger.error(e)
