# -*- coding: utf-8 -*-
# Created by coder-zhuyu on 2018/9/6
"""
    元库管理
"""
from utils.db import Db
from ..request_handler import BaseRequestHandler
from ..log import debug_log, info_log, warning_log, error_log
from utils.size_convert import convert_bytes, convert_count
from ..route import route


@route('/table/(.+)/(.+)')
class TableHandler(BaseRequestHandler):
    async def get(self, conn_name, table_name):
        db_name = await Db.get_db_name_by_conn(conn_name)
        debug_log(db_name)

        data = {}

        rows, row_count = await Db.select(
            "select table_name, table_rows, data_length, create_time, table_comment "
            "from information_schema.tables where table_schema=%s and table_name=%s",
            (db_name, table_name),
            db_conn_name=conn_name
        )

        records = []
        for row in rows:
            records.append({
                'table_name': row['table_name'],
                'row_count': row['table_rows'],
                'table_size': convert_bytes(int(row['data_length'])),
                'create_time': str(row['create_time']),
                'create_user': 'admin',
                'table_comment': row['table_comment']
            })

        data['records'] = records
        data['page_num'] = 1
        data['total_num'] = 1
        data['total_page'] = 1

        self.response_json(data=data)
