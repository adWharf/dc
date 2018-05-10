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
from dc.core import db, config, logger
from .bowler import Bowler
from .commander import Commander
from dc.models import Model, Strategy, Filter, HistoryFilter, Trim, Action

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
                actions = []
                for strategy in strategies:
                    if not self._filter(data, strategy):
                        continue
                    if not self._history_filter(data, strategy):
                        continue
                    actions.append(self._parse_actions(data, strategy))
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

    def _filter(self, data, strategy: Strategy):
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

    def _history_filter(self, data, strategy: Strategy):
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
            pass
        return actions


