# -*- coding: utf-8 -*-
from utils.db import Db
from ..request_handler import BaseRequestHandler
from ..route import route


@route('/user/([0-9]+)')
class UserHandler(BaseRequestHandler):
    async def get(self, user_id):
        # check token的user_id 和 user_id是否一致 不一致返回403
        self.check_user_id(user_id)

        result, row_count = await Db.select("SELECT id, username, mobile FROM user where id=%s limit 1", int(user_id))
        if result is None:
            self.response_json(code=600100)
        else:
            self.response_json(data=result)

    # async def put(self, user_id):
    #     self.check_user_id(user_id)
    #
    #     mobile = self.get_argument('mobile')
    #     name = self.get_argument('username')
    #
    #     Regex(r'^1[3-9][0-9]{9}$').validate(mobile)
    #     Schema(str).validate(name)
    #
    #     affected_rows = await Db.update("UPDATE user set mobile=%s, username=%s where id=%s",
    #                                     (mobile, name, int(user_id)))
    #     debug_log(affected_rows)
    #     if not affected_rows:
    #         self.response_json(code=600101)
    #     else:
    #         self.response_json()
