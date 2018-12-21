# -*- coding: utf-8 -*-

from .codemsg import CodeMsg


class ValidationError(ValueError):
    pass


class UserIDException(Exception):
    def __init__(self):
        Exception.__init__(self, 'user_id not equal')


class NoDBConnectConfigException(Exception):
    def __init__(self):
        Exception.__init__(self, 'no db conn_name config')


class DBConnFaild(Exception):
    def __init__(self):
        Exception.__init__(self, CodeMsg._code_msg[602000])
