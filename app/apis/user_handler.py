# -*- coding: utf-8 -*-

from app.apis.filter_request_handler import CFilterRequestHandler
from app.route import route
from utils.db import GloabalDB


@route('/user/([0-9]+)')
class UserHandler(CFilterRequestHandler):
    pass
    # async def get(self, user_id):
    #     # check token的user_id 和 user_id是否一致 不一致返回403
    #     self.check_user_id(user_id)
    #
    #     result, row_count = await Db.select("SELECT id, username, mobile FROM user where id=%s limit 1", int(user_id))
    #     if result is None:
    #         self.response_json(code=600100)
    #     else:
    #         self.response_json(data=result)
