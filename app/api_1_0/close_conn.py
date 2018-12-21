# -*- coding: utf-8 -*-
from utils.db import CDB
from ..request_handler import BaseRequestHandler
from ..route import route


@route('/close_conn')
class CloseConnHandler(BaseRequestHandler):

    async def post(self, *args, **kwargs):
        uid = self.request.headers.get('Uid', '')
        if uid is None or uid != '5115':
            return self.response_json(code=401002)
            CDB.close_conn()
        return self.response_json()
