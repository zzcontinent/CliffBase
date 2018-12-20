# -*- coding: utf-8 -*-
# Created by coder-zhuyu on 2018/9/5
"""
    元库管理
"""
from collections import defaultdict
from utils.db import Db
from ..request_handler import BaseRequestHandler
from ..route import route


@route('/dbs')
class DBSHandler(BaseRequestHandler):
    async def get(self):
        rows, row_count = await Db.select(
            "SELECT db_config_id, conn_name, env, host, db_name "
            "FROM db_config "
            "where conn_type=0 and is_enabled=1 and is_display=1"
        )

        data = defaultdict(list)
        for row in rows:
            data[row['env']].append(row)

        self.response_json(data=data)
