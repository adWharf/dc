#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: bridge.py
@time: 08/04/2018 15:54
"""

import json
import multiprocessing
from werkzeug.datastructures import Headers
from flask import Flask, request, Response as BaseResponse
from dc.core import config


class Response(BaseResponse):
    def __init__(self, response=None, **kwargs):
        kwargs['headers'] = ''
        headers = kwargs.get('headers')
        origin = ('Access-Control-Allow-Origin', '*')
        methods = ('Access-Control-Allow-Methods', 'HEAD, OPTIONS, GET, POST, DELETE, PUT')
        extra = ('Access-Control-Allow-Headers', '*')
        if headers:
            headers.add(*origin)
            headers.add(*methods)
            headers.add(*extra)
        else:
            headers = Headers([origin, methods, extra])
        kwargs['headers'] = headers
        super().__init__(response, **kwargs)


_bridge = Flask(__name__)
_bridge.response_class = Response
global _data_q  # type: multiprocessing.Connection
global _command_q  # type: multiprocessing.Connection

TYPE_STATISTIC = 1
TYPE_CAMP_INFO = 2


def set_client(ct):
    global client
    client = ct


@_bridge.route('/processedStatistic', methods=['POST'])
def data_receiver():
    global _data_q
    _data_q.send_bytes(bytes(json.dumps({request.form}), encoding='utf-8'))


def run(data_q, command_q):
    global _data_q, _command_q
    _data_q = data_q
    _command_q = command_q
    _bridge.run(host='0.0.0.0', port=config.get('app.schedule.bowler.httpbowler.port'))

