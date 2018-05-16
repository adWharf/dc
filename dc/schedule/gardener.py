#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: gardener.py
@time: 03/05/2018 23:01
"""
import random
import json
import pycron
import pendulum
from dc.core import db, config, logger
from .bowler import Bowler
from .commander import Commander
from dc.models import Model, Strategy, Filter, HistoryFilter, \
    Trim, Action, Campaign, WXCampaign, Point, CampaignHelper
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


def build_command(data, action, val):
    return {
        'campaign_id': data['campaign_id'],
        'action': action,
        'value': val
    }


class Gardener(object):
    def __init__(self, bowler: Bowler, commander: Commander):
        self._bowler = bowler
        self._commander = commander
        self._db = db.get_mysql_client(config.get('app.db.mysql'))
        self._mongo = db.get_mongo_client(config.get('app.db.mongo'))
        Model.set_connection_resolver(self._db)

    def trim(self):
        camp_model = Campaign(self._mongo)
        for data in self._bowler:
            try:
                # Only active campaign need to trim
                if data['status'] != ADSTATUS_NORMAL:
                    continue

                strategies = Strategy.where('account_id', data['account_id']).get()
                # actions = []

                campaign = camp_model.find(data['campaign_id'])
                if not campaign:
                    logger.notice('Campaign info not found for [%d]' % data['campaign_id'])
                    continue

                wxcampaign = WXCampaign(campaign)
                actions = self._filter(data, strategies, wxcampaign)
                # for strategy in strategies:
                #     if not self._filter(data, strategy, wxcampaign):
                #         continue
                #     if not self._history_filter(data, strategy, wxcampaign):
                #         continue
                #     actions.append(self._parse_actions(data, strategy))
                commands = []
                for act in actions:
                    action = Action()
                    action.campaign_id = data['campaign_id']
                    action.action = act['action']
                    action.value = act['value']
                    action.triggered_point = json.dumps(data)
                    action.account_id = data['account_id']
                    action.save()
                    commands.append(action.serialize())
                if len(commands) == 0:
                    commands.append(build_command(data, 'timeset_end', random.randint(6, 20)))
                if len(commands) > 0:
                    self._commander.transmit({
                        'target': 'client',
                        'client': data['agency'],
                        'commands': commands
                    })
                    logger.info('Campaign [%d] should be trimmed, send action successfully' % data['campaign_id'])

            except Exception as e:
                logger.error('Exception occurred when handle data [%s]' % json.dumps(data))
                logger.error(e)

    def _filter(self, data, strategies, wxcampaign: CampaignHelper):
        # today = pendulum.today().to_datetime_string()
        # yesterday = pendulum.yesterday().to_datetime_string()
        # yesterday_count = Point.where('created_at', '<', today)\
        #     .where('created_at', '>', yesterday)\
        #     .where('campaign_id', data['campaign_id'])\
        #     .where('status', ADSTATUS_NORMAL)\
        #     .order_by('id', 'desc')\
        #     .first()
        #
        # before_yesterday_count = Point.where('created_at', '<', yesterday)\
        #     .where('campaign_id', data['campaign_id']) \
        #     .where('status', ADSTATUS_NORMAL)\
        #     .order_by('id', 'desc')\
        #     .first()
        today = pendulum.today()
        yesterday = pendulum.yesterday()
        now = pendulum.now()
        actions = []
        delivery_start_time, delivery_end_time = wxcampaign.delivery_time()
        cur_hour = now.hour

        may_missing_key = ['1day_action_step', '1day_action_reversion', '1day_action_complete_order',
                           '1day_action_complete_order_amount']
        for key in may_missing_key:
            if key not in data:
                data[key] = 0

        if delivery_start_time >= yesterday:
            '''
            凌晨1点-2点，新计划指最近一天建立的，
            话费／点击次数>10 || （当天花费>190 且没有订单）， 生效时间改到6点
            '''
            if (int(data['click_count']) == 0 or int(data['total_cost']) / 100 / int(data['click_count']) > 10) or \
                    (data['total_cost'] > 19000 and data['1day_action_complete_order'] == 0):
                actions.append(build_command(data, 'timeset_end', 6))
        elif yesterday <= delivery_start_time < today:
            '''
            次新计划，满足上述条件直接暂停
            '''
            if (int(data['click_count']) == 0 or int(data['total_cost']) / 100 / int(data['click_count']) > 10) or \
                    (data['total_cost'] > 19000 and data['1day_action_complete_order'] == 0):
                actions.append(build_command(data, 'suspend', None))
        else:
            statistic = Point.select(Point.raw('max(1day_action_complete_order) as order_num, '
                                               'max(1day_action_complete_order_amount) as order_amount'))\
                .where('created_at', '>=', today)\
                .where('campaign_id', data['campaign_id'])\
                .where('status', ADSTATUS_NORMAL)\
                .first()
            order_amount = max(statistic.order_amount, data['1day_action_complete_order_amount'], 0)
            order_num = max(statistic.order_num, data['1day_action_complete_order'], 0)
            data['sy_cost'] = int(data['sy_cost'])
            ori = 0 if order_amount == 0 else data['sy_cost'] / order_amount
            if wxcampaign.is_beishang():
                '''
                晨1点-2点，定向为仅包含北上的计划，roi低于1.5 且订单个数<2，设置7点， 
                roi<1.5 && 订单个数>=2  设置到10点
                '''
                if order_num < 2 and ori < 1.5:
                    actions.append(build_command(data, 'timeset_end', 7))
                elif order_num > 4 and ori < 1.5:
                    actions.append(build_command(data, 'timeset_end', 10))
            else:
                '''
                1-2点，定向非北上城市，（当天花费 > 200 且 历史转换为0） 暂停，
                （花费> 200 历史总花费／历史总转化 >= 1.5） 设置到9点
                （花费> 200 历史总花费／历史总转化 < 1.5） 设置到7点
                '''
                records = Point.select(Point.raw('max(sy_cost) as day_cost, '
                                                 'max(1day_action_complete_order) as order_num, '
                                                 'max(1day_action_complete_order_amount) as order_amount'))\
                    .where('created_at', '>=', today.to_datetime_string()) \
                    .where('campaign_id', data['campaign_id']) \
                    .group_by(Point.raw('DATE_FORMAT(update_time, "%%Y%%m%%d")')) \
                    .get()
                total_cost = 0
                total_order = 0
                total_order_amount = 0
                for record in records:
                    total_cost += int(record.day_cost)
                    total_order += record.order_num
                    total_order_amount += record.order_amount
                transfer_rate = 0 if total_order == 0 else total_cost / total_order
                if data['sy_cost'] > 200:
                    if total_order == 0:
                        actions.append(build_command(data, 'suspend', None))
                    elif transfer_rate >= 1.5:
                        actions.append(build_command(data, 'timeset_end', 9))
                    else:
                        actions.append(build_command(data, 'timeset_end', 7))
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


