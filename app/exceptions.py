# -*- coding: utf-8 -*-

from .codemsg import CodeMsg

from .log import debug_log, info_log, warning_log, error_log


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
        from utils.db import Db
        Db.close_conn()
        error_log('连接异常，关闭所有连接')
