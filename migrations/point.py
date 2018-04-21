#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: point.py
@time: 21/04/2018 18:34
"""
from orator import Schema


def migrate(schema: Schema):
    with schema.create('points') as table:
        table.big_increments('id')
        table.string('agency')
        table.string('account').nullable()
        table.string('account_id').nullable()
        table.big_integer('campaign_id').nullable()
        table.big_integer('ad_group_id').nullable()
        table.big_integer('creative_id').nullable()
        table.big_integer('aid').nullable()
        table.string('cname')
        table.decimal('total_cost')
        table.big_integer('view_count')
        table.big_integer('click_count')
        table.small_integer('status').default(0)
        table.decimal('sy_cost').default(0.00)
        # 二跳
        table.big_integer('1day_action_step').default(0)
        # 预约量
        table.big_integer('1day_action_reversion').default(0)
        # 激活
        table.big_integer('1day_action_activate_app').default(0)
        # 下单
        table.big_integer('1day_action_complete_order').default(0)
        # 下单金额
        table.big_integer('1day_action_complete_order_amount').default(0)
        table.timestamp('update_time')
        table.timestamps()


def rollback(schema: Schema):
    schema.drop('points')
