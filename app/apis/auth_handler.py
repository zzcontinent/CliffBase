# -*- coding: utf-8 -*-
from app.apis.filter_request_handler import CFilterRequestHandler
from utils.log import debug_log
from schema import Schema
import concurrent.futures
import bcrypt
import tornado
import tornado.escape
import tornado.web
import asyncio
import datetime
import time
from app.route import route

# A thread pool to be used for password hashing with bcrypt.
executor = concurrent.futures.ThreadPoolExecutor(2)


@route('/auth/login')
class AuthLoginHandler(CFilterRequestHandler):
    """Auth login."""

    # async def post(self):
    #     # user_name = self.get_argument('username')
    #     # password = self.get_argument('password')
    #     user_name = self.get_json_data('username')
    #     password = self.get_json_data('password')
    #
    #     Schema(str).validate(user_name)
    #     Schema(str).validate(password)
    #
    #     result, row_count = await Db.select_one("SELECT * FROM user where username=%s limit 1", user_name)
    #     debug_log(result)
    #     if not result or not row_count:
    #         self.response_json(code=401001)
    #         return
    #
    #     # check password
    #     job = executor.submit(bcrypt.hashpw, tornado.escape.utf8(password), tornado.escape.utf8(result['password']))
    #     hashed_password = tornado.escape.to_unicode(await asyncio.wrap_future(job))
    #
    #     if hashed_password == result['password']:
    #         now = datetime.datetime.now()
    #         data = {
    #             'uid': result['id'],
    #             'exp': int(time.mktime((now + datetime.timedelta(seconds=config.token_exp_delta)).timetuple())),
    #             'at': int(time.mktime(now.timetuple())),
    #         }
    #         token = token_encode(data)
    #         data['token'] = token
    #         self.response_json(data=data)
    #     else:
    #         self.response_json(code=401001)

