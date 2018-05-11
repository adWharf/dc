#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: wxcampaign.py
@time: 10/05/2018 16:32
"""
import json
from .campaign import Campaign
from dc.core import logger
from dc.constants.ad import AD_BID_TYPE, AD_BID_TYPE_OCPM_OPT_MORE_CLICK, AD_BID_TYPE_OCPM_OPT_MORE_ORDER

logger = logger.get('Models.WXCampaign')


class WXCampaign(Campaign):
    def __init__(self, campaign):
        self._campaign = campaign

    def is_beishang(self):
        '''
        定向城市是否为北京上海
        :return:
        '''
        try:
            beijing = 110000
            shanghai = 310000
            areas = json.loads(self._campaign['target_groups'][0]['ad_groups'][0]['ad_target']['area'])
            if beijing in areas and shanghai in areas:
                return True
            return False
        except Exception as e:
            logger.error(e)
            return False

    def bid_type(self):
        try:
            ad_group = self._campaign['target_groups'][0]['ad_groups'][0]['ad_group']
            if not ad_group:
                return None, None
            if 'strategy_opt' not in ad_group:
                return AD_BID_TYPE.CPM, None
            opt = json.loads(ad_group['strategy_opt'])
            if opt['bid_action_type'] == AD_BID_TYPE_OCPM_OPT_MORE_ORDER:
                return AD_BID_TYPE.OCPM, AD_BID_TYPE_OCPM_OPT_MORE_ORDER
            elif opt['bid_action_type'] == AD_BID_TYPE_OCPM_OPT_MORE_CLICK:
                return AD_BID_TYPE.OCPM, AD_BID_TYPE_OCPM_OPT_MORE_CLICK
        except Exception as e:
            logger.error(e)
            return None, None


