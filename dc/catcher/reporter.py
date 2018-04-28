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
import pendulum
from dc.core import cache, logger, config
import requests
from .catcher import Catcher

logger = logger.get('Catcher.Reporter')


def fetch_order_info(start, end):
    resp = requests.get(config.get('app.api.order.url') % (start, end))
    if resp.status_code/100 == 2:
        return json.loads(resp.content)


def connect_order(ads, order, prefix=''):
    for ad in ads:
        if ad['cname'] in order:
            ad['1day_action_step'] = order[ad['cname']]['step']
            ad['1day_action_reversion'] = order[ad['cname']]['unpaid']
            ad['1day_action_complete_order'] = order[ad['cname']]['paid']
            ad['1day_action_complete_order_amount'] = order[ad['cname']]['amount']
    return ads


class Reporter(Catcher):
    '''

    '''
    def __init__(self):
        logger.info('Init Reporter...')
        Catcher.__init__(self)
        kafka_server = '%s:%d' % (config.get('app.kafka.host'), config.get('app.kafka.port'))
        logger.info('Try to connect to kafka...')
        self._consumer = KafkaConsumer('ad.original.statistic',
                                       client_id='ad_statistic_catcher_reporter',
                                       group_id='ad_statistic_catcher',
                                       bootstrap_servers=kafka_server)
        logger.info('Connect to kafka successfully')
        for msg in self._consumer:
            try:
                data = json.loads(msg.value)
                if cache.get('dc.catcher.reporter.%s.%s' % (data['account'], data['update_time'])):
                    continue
                account_name = data['account']
                account = self._db.table('accounts').where('name', account_name).first()
                if not account:
                    continue
                order_data = fetch_order_info(data['update_time'][:10] + ' 00:00:00', data['update_time'])
                records = connect_order(data['data'], order_data)
                points = []
                avai_fields = ['total_cost', 'view_count', 'sy_cost', 'click_count', '1day_action_step',
                              '1day_action_reversion', '1day_action_complete_order', '1day_action_complete_order_amount']
                avai_tags = ['account', 'cname']
                with self._db.transaction():
                    for record in records:
                        fields = {}
                        tags = {}
                        record['account'] = account_name
                        record['account_id'] = account['id']
                        for key in avai_fields:
                            if key in record:
                                fields[key] = float(record[key])
                        for key in avai_tags:
                            if key in record:
                                tags[key] = str(record[key])
                        points.append({
                            'measurement': record['agency'],
                            'tags': tags,
                            'time': pendulum.from_format(record['update_time'], '%Y-%m-%d %H:%M:%S'),
                            'fields': fields
                        })
                        self._db.table('points').insert(record)
                self._influxdb.write_points(points)
            except Exception as e:
                raise e
                logger.error(e)


