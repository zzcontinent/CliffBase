# -*- coding: utf-8 -*-
# Created by coder-zhuyu on 2018/9/6
"""
    元库管理
"""
from utils.db import Db
from ..request_handler import BaseRequestHandler
from ..log import debug_log, info_log, warning_log, error_log
from utils.size_convert import convert_bytes, convert_count
from utils.page import get_total_page
from ..route import route


@route('/db/(.+)')
class DBHandler(BaseRequestHandler):
    async def get(self, conn_name):
        db_name = await Db.get_db_name_by_conn(conn_name)
        debug_log(db_name)

        data = {}

        row, row_count = await Db.select_one(
            "select count(table_name) as table_count from information_schema.tables where table_schema=%s",
            db_name,
            conn_name
        )
        data['table_count'] = row['table_count']

        row, row_count = await Db.select_one(
            "select count(column_name) as column_count from information_schema.columns where table_schema=%s",
            db_name,
            conn_name
        )
        data['column_count'] = row['column_count']

        row, row_count = await Db.select_one(
            "select coalesce(sum(table_rows), 0) as row_count, coalesce(sum(data_length), 0) as db_size "
            "from information_schema.tables where table_schema=%s",
            db_name,
            conn_name
        )
        data['row_count'] = convert_count(int(row['row_count']))
        data['db_size'] = convert_bytes(int(row['db_size']))

        self.response_json(data=data)


@route('/tables/(.+)')
class TablesHandler(BaseRequestHandler):
    async def get(self, conn_name):
        # 分页
        page_num = self.get_argument('page_num', 1)
        page_size = self.get_argument('page_size', 10)
        page_num = int(page_num)
        page_size = int(page_size)

        db_name = await Db.get_db_name_by_conn(conn_name)
        debug_log(db_name)

        data = {}

        rows, _ = await Db.select_one(
            "select count(table_name) as table_count "
            "from information_schema.tables where table_schema=%s",
            db_name,
            db_conn_name=conn_name
        )

        table_count = int(rows['table_count'])
        debug_log(table_count)
        if table_count == 0:
            self.response_json(data=data)
            return

        rows, row_count = await Db.select(
            "select table_name, table_rows, data_length, create_time, table_comment "
            "from information_schema.tables where table_schema=%s limit %s offset %s",
            (db_name, page_size, (page_num-1)*page_size),
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
        data['page_num'] = page_num
        data['total_num'] = table_count
        data['total_page'] = get_total_page(page_size, table_count)

        self.response_json(data=data)
