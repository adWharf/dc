#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: reporter.py
@time: 10/04/2018 16:14
"""
import json
from kafka import KafkaConsumer
from core import config, db, logger, cache
import requests
import pendulum
from catcher.catcher import Catcher


def fetch_order_info(start, end):
    resp = requests.get(config.get('app.api.order.url') % (start, end))
    if resp.status_code/100 == 2:
        return json.loads(resp.content)


def connect_order(ads, order, prefix=''):
    for ad in ads:
        if ad['cname'] in order:
            pass

    return ads


class Reporter(Catcher):
    def __init__(self):
        Catcher.__init__(self)
        kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
        self._consumer = KafkaConsumer('ad.original.statistic',
                                       client_id='ad_statistic_catcher',
                                       group_id='ad_statistic_catcher',
                                       bootstrap_servers=kafka_server)
        for msg in self._consumer:
            try:
                data = json.loads(json.loads(msg.value))
                if cache.get('dc.catcher.reporter.%s.%s' % (data['account'], data['update_at'])):
                    continue
                order_data = fetch_order_info(pendulum.today('local').to_datetime_string(), data['updated_at'])
                records = connect_order(data, order_data)
                self._db.table('records').save(records)
                self._consumer.commit()
            except Exception as e:
                logger.error(e)


