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

