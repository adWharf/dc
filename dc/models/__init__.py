#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: __init__.py.py
@time: 10/05/2018 16:32
"""
from .models import *
from .campaign import CampaignHelper
from .wxcampaign import WXCampaign
from dc.core import db, config

_conn = db.get_mysql_client(config.get('app.db.mysql'))
Model.set_connection_resolver(_conn)
