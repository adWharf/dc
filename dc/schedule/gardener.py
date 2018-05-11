#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: gardener.py
@time: 03/05/2018 23:01
"""
import json
import pycron
import pendulum
from dc.core import db, config, logger
from .bowler import Bowler
from .commander import Commander
from dc.models import Model, Strategy, Filter, HistoryFilter, \
    Trim, Action, Campaign, WXCampaign, Point
from dc.constants.ad import ADSTATUS_NORMAL

logger = logger.get('Schedule.Gardener')

OP_EQ = '='
OP_NEQ = '!='
OP_GT = '>'
OP_EGT = '>='
OP_LT = '<'
OP_ELT = '<='

TYPE_STR = 'string'
TYPE_INT = 'int'
TYPE_DOUBLE = 'double'

InvalidType = None


def _cast_to(val, tp):
    if tp == TYPE_STR:
        return str(val)
    elif tp == TYPE_INT:
        return int(val)
    elif tp == TYPE_DOUBLE:
        return float(val)
    else:
        logger.error('Invalid type when cast [%s] to [%s]' % (val, tp))
        raise InvalidType


class Gardener(object):
    def __init__(self, bowler: Bowler, commander: Commander):
        self._bowler = bowler
        self._commander = commander
        self._db = db.get_mysql_client(config.get('app.db.mysql'))
        Model.set_connection_resolver(self._db)

    def trim(self):
        for data in self._bowler:
            try:
                strategies = Strategy.where('account_id', data['account_id']).get()
                # actions = []
                wxcampaign = WXCampaign(Campaign.find(data['cid']))
                actions = self._filter(data, strategies, wxcampaign)
                # for strategy in strategies:
                #     if not self._filter(data, strategy, wxcampaign):
                #         continue
                #     if not self._history_filter(data, strategy, wxcampaign):
                #         continue
                #     actions.append(self._parse_actions(data, strategy))
                if len(actions) > 0:
                    action = Action()
                    action.campaign_id = data['campaign_id']
                    action.action = json.dumps(actions)
                    action.triggered_point = json.dumps(data)
                    action.account_id = data['account_id']
                    action.save()
                    self._commander.transmit({
                        'target': 'client',
                        'client': data['agency'],
                        'actions': actions
                    })
            except Exception as e:
                logger.error('Exception occurred when handle data [%s]' % json.dumps(data))
                logger.error(e)

    def _filter(self, data, strategies, wxcampaign: WXCampaign):
        today = pendulum.today().to_datetime_string()
        yesterday = pendulum.yesterday().to_datetime_string()
        yesterday_count = Point.where('created_at', '<', today)\
            .where('created_at', '>', yesterday)\
            .where('campaign_id', data['cid'])\
            .where('status', ADSTATUS_NORMAL)\
            .first()

        before_yesterday_count = Point.where('created_at', '<', yesterday)\
            .where('campaign_id', data['campaign_id']) \
            .where('status', ADSTATUS_NORMAL) \
            .first()
        actions = []
        if not yesterday_count and (not before_yesterday_count):
            '''
            凌晨1点-2点，新计划指最近一天建立的，
            话费／点击次数>10 || （当天花费>190 且没有订单）， 生效时间改到6点
            '''
            if data['total_cost']/100 / data['click_count'] > 10 or \
                    (data['total_cost'] > 19000 and data['1day_action_complete_order'] == 0):
                actions.append({
                        'action': 'timeset_end',
                        'value': 6,
                    })
        elif (not before_yesterday_count) and yesterday_count:
            '''
            次新计划，满足上述条件直接暂停
            '''
            if data['total_cost']/100 / data['click_count'] > 10 or \
                    (data['total_cost'] > 19000 and data['1day_action_complete_order'] == 0):
                actions.append({
                    'action': 'suspend',
                    'value': None
                })
        else:
            statistic = Point.select(Point.raw('sum(1day_action_complete_order) as order_num, '
                                               'sum(1day_action_complete_order_amount) as order_amount)'))\
                .where('created_at', '>=', today)\
                .where('campaign_id', data['cid'])\
                .where('status', ADSTATUS_NORMAL)\
                .get()
            ori = data['sy_cost'] / statistic['order_amount']
            if wxcampaign.is_beishang():
                '''
                晨1点-2点，定向为仅包含北上的计划，roi低于1.5 且订单个数<2，设置7点， 
                roi<1.5 && 订单个数>=2  设置到10点
                '''
                if statistic['order_num'] < 2 and ori < 1.5:
                    actions.append({
                        'action': 'timeset_end',
                        'value': 7,
                    })
                elif statistic['order_num'] > 4 and ori < 1.5:
                    actions.append({
                        'action': 'timeset_end',
                        'value': 10,
                    })
            else:
                '''
                1-2点，定向非北上城市，（当天花费 > 200 且 历史转换为0） 暂停，
                （花费> 200 历史总花费／历史总转化 >= 1.5） 设置到9点
                （花费> 200 历史总花费／历史总转化 < 1.5） 设置到7点
                '''
                records = Point.select(Point.raw('max(sy_cost) as day_cost, max(1day_action_complete_order) as order_num, '
                                       'max(1day_action_complete_order_amount) as order_amount'))\
                    .where('created_at', '>=', today) \
                    .where('campaign_id', data['cid']) \
                    .group_by(Point.raw('DATE_FORMAT(update_time, "%Y%m%d")')) \
                    .get()
                total_cost = 0
                total_order = 0
                total_order_amount = 0
                for record in records:
                    total_cost += record['day_cost']
                    total_order += record['order_num'],
                    total_order_amount += record['order_amount']
                transfer_rate = total_cost / total_order
                if data['sy_cost'] > 200:
                    if total_order == 0:
                        actions.append({
                            'action': 'suspend',
                            'value': None
                        })
                    elif transfer_rate >= 1.5:
                        actions.append({
                            'action': 'timeset_end',
                            'value': 9,
                        })
                    else:
                        actions.append({
                            'action': 'timeset_end',
                            'value': 7,
                        })
        return actions


    def _attr_filter(self, data, strategy: Strategy, wxcampaign: WXCampaign):
        if not strategy:
            return False
        # Check worktime
        if strategy.worktime and (not pycron.is_now(strategy.worktime)):
            return False

        # Check according to the attr of data
        for record in strategy.records:
            key = data[record.key]
            val = _cast_to(record.value, record.type)
            if record.op == OP_EQ:
                if not (key == val):
                    return False
            elif record.op == OP_NEQ:
                if not (key != val):
                    return False
            elif record.op == OP_GT:
                if not (key > val):
                    return False
            elif record.op == OP_EGT:
                if not (key >= val):
                    return False
            elif record.op == OP_LT:
                if not (key < val):
                    return False
            elif record.op == OP_ELT:
                if not (key <= val):
                    return False
            else:
                logger.error('Invalid op of filter[%d]' % record.id)
                return False
        return True

    def _history_filter(self, data, strategy: Strategy, wxcampaign: WXCampaign):
        # TODO support history record
        history_filters = strategy.history_filters
        for record in history_filters:
            pass
        return False

    def _parse_actions(self, data, strategy: Strategy):
        '''
        目前支持修改出价／修改生效时间
        :param data:
        :param strategy:
        :return:
        '''
        trims = strategy.trims
        actions = []
        for trim in trims:
            if trim.action == 'modify_timeset':
                if trim.key == 'end':
                    actions.append({
                        'action': 'timeset_end',
                        'value': trim.value,
                    })
            elif trim.action == 'suspend_camp':
                actions.append({
                    'action': 'suspend',
                    'value': None
                })
            else:
                logger.error('Unknow trim [%s]' % json.dumps(trim))
        return actions


