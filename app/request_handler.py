# -*- coding: utf-8 -*-
from tornado.web import RequestHandler
import json
from utils.db import Db
from utils.token import decode as token_decode
from jwt.exceptions import ExpiredSignatureError
from .exceptions import *
import schema

not_need_token_urls = {
    '/auth/login',
    '/close_conn',
}


class BaseRequestHandler(RequestHandler):
    """Base class for HTTP request handlers.

    Override the method get_current_user in coroutine.
    Add a method response_json for HTTP json response.
    """

    async def prepare(self):
        """Called at the beginning of a request before  `get`/`post`/etc."""
        # token check
        await self.__token_check_middleware()
        debug_log(self.request)
        self.__body_data = self.request.body.decode('utf8')
        try:
            self.__body_data_dict = json.loads(self.__body_data)
            info_log('request body: %s', self.__body_data)
        except Exception as e:
            self.__body_data_dict = {}
            info_log('request body: %s', self.__body_data)

    def get_json_data(self, key):
        return self.__body_data_dict.get(key, None)

    async def get_current_user(self):
        """Override to determine the current user from, e.g., a cookie."""
        user_id = self.request.headers.get('Uid', '')
        if not user_id:
            return None
        result, _ = await Db.select_one("SELECT * FROM user where id=%s limit 1", int(user_id))
        debug_log(result)
        return result

    def get_user_id(self):
        user_id = self.request.headers.get('Uid', 0)
        return int(user_id)

    def check_user_id(self, user_id):
        if self.get_user_id() != int(user_id):
            raise UserIDException

    def response_json(self, data=None, code=0, status=200):
        """HTTP response in the form of json.
        pass

        :param data: return body
        :param code: return code
        :param status: http status
        :return:
        """
        resp_dict = {
            'code': code,
            'msg': CodeMsg.get_msg(code)
        }

        if data is not None:
            resp_dict['data'] = data
        else:
            resp_dict['data'] = {}

        self.set_status(status)
        self.set_header('Content-Type', 'application/json; charset=utf-8')

        self.write(json.dumps(resp_dict, ensure_ascii=False))

    def write_error(self, status_code, **kwargs):
        """Override error handler."""
        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]
            if isinstance(exception, UserIDException):
                self.response_json(code=403000)
                return
            elif isinstance(exception, DBConnFaild):
                self.response_json(code=602000)
                return
            elif isinstance(exception, NoDBConnectConfigException):
                self.response_json(code=404000)
                return
            elif isinstance(exception, schema.SchemaMissingKeyError):
                self.response_json(code=400001)
                return
            elif isinstance(exception, schema.SchemaError):
                self.response_json(code=400002)
                return
        code = int(str(status_code) + '000')

        self.response_json(code=code, status=status_code)

    async def __token_check_middleware(self):
        """Called at the beginning of a request before  `get`/`post`/etc."""
        if self.request.uri in not_need_token_urls:
            return

        # token 校验
        token = self.request.headers.get('Token', '')
        user_id = self.request.headers.get('Uid', '')
        if not token or not user_id:
            error_log('request header中缺少token或者uid')
            self.response_json(code=401002)
            self.finish()
            return

        try:
            payload = token_decode(token)
        except ExpiredSignatureError as e:
            error_log('token过期')
            self.response_json(code=401003)
            self.finish()
            return

        if payload['uid'] != int(user_id):
            error_log('request header中的uid和token中的不同')
            self.response_json(code=401004)
            self.finish()
            return

        user = await self.get_current_user()
        if not user:
            self.response_json(code=401001)
            self.finish()
            return

