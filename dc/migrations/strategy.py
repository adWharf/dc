#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: strategy.py
@time: 03/05/2018 16:27
"""
from orator import Schema


def migrate(schema: Schema):
    if schema.has_table('trim_strategies'):
        return
    with schema.create('trim_strategies') as table:
        table.big_increments('id')
        table.big_integer('account_id')
        table.string('name')
        table.string('worktime')
        table.small_integer('is_repeat')        # worktime内是否重复生效
        table.timestamps()

    '''
    对当前Point进行过滤
    '''
    with schema.create('trim_filters') as table:
        table.big_increments('id')
        table.big_integer('strategy_id')
        table.string('type').default('string')  # 类型 string/int/double/
        table.string('key')
        table.string('op')
        table.string('value')
        table.text('extra')
        table.timestamps()

    '''
    需要历史数据介入进行过滤
    '''
    with schema.create('trim_history_filters') as table:
        table.big_increments('id')
        table.big_integer('strategy_id')
        table.string('type').default('string')  # 类型 string/int/double/
        table.small_integer('day')              # 参与过滤的天数数据
        table.string('aggregate').nullable()    # 聚合函数 支持sum／avg／latest／earliest
        table.string('key')
        table.string('op')
        table.string('value')
        table.text('extra')
        table.timestamps()


    '''
    触发相应条件时需要执行的对应修改操作
    '''
    with schema.create('trims') as table:
        table.big_increments('id')
        table.big_integer('strategy_id')
        table.small_integer('type').default(1)      # 类型
        table.string('level').default('campaign')           # 操作级别 campaign/adgroup/ad
        table.string('action')
        table.string('value')
        table.text('extra1').nullable()
        table.text('extra2').nullable()
        table.text('extra3').nullable()
        table.timestamps()

    '''
    策略对应的修改动作，以及执行结果的反馈
    '''
    with schema.create('trim_actions') as table:
        table.big_increments('id')
        table.big_integer('account_id')
        table.big_integer('campaign_id')
        table.text('action')                            # 具体调整内容
        table.text('triggered_point').nullable()        # 触发该action的记录
        table.text('resp_cnt').nullable()
        table.string('resp_status_code').nullable()
        table.timestamps()


def rollback(schema: Schema):
    schema.drop('trim_strategies')
    schema.drop('trim_filters')
    schema.drop('trim_history_filters')
    schema.drop('trims')
    schema.drop('trim_actions')
