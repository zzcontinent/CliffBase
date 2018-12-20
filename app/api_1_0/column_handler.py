# -*- coding: utf-8 -*-
from utils.db import Db
from ..request_handler import BaseRequestHandler
from app.route import route


def convertStr(in_param):
    if in_param is None:
        return 'Null'
    else:
        return str(in_param)


@route('/table/column')
class ColumnHandler(BaseRequestHandler):

    async def post(self, *args, **kwargs):
        conn_name = self.get_json_data('conn_name')
        table_name = self.get_json_data('table_name')
        if conn_name is None or table_name is None:
            return self.response_json(code=400001)
        db_name = await Db.get_db_name_by_conn(conn_name)
        # 数据库里的列信息
        sql_col = u'''SELECT 
table_schema,
table_name,
column_name,
column_default,
is_nullable,
column_type,
column_key,
column_comment 
FROM information_schema.`COLUMNS` where table_schema = '{0}' and table_name = '{1}' '''.format(db_name, table_name)
        result, row_count = await Db.select(query=sql_col, db_conn_name=conn_name)

        # 数据库里的表信息
        sql_table = u'''select CREATE_TIME,UPDATE_TIME from information_schema.`TABLES` where table_schema = '{0}' and table_name ='{1}' '''.format(
            db_name, table_name)

        result_table, row_count_table = await Db.select(query=sql_table, db_conn_name=conn_name)

        # 元数据管理系统里的同步信息
        sql_metadata = u''' SELECT db_info_id,job_name,db_name,table_name,column_name,CREATE_TIME,updated_tm FROM `db_info` where db_name = '{0}' and table_name='{1}' and sync_cnt in(
SELECT max(sync_cnt) as sync_cnt FROM `db_info` where db_name = '{0}' and table_name='{1}' )'''.format(
            db_name + '@' + conn_name, table_name)
        result_metadata, row_count_metadata = await Db.select(query=sql_metadata)

        # 创建时间
        create_tm = ''
        for row in result_table:
            create_tm = row['CREATE_TIME']
        # 更新时间
        update_tm = dict()
        for row in result_metadata:
            update_tm[row['column_name']] = row['updated_tm']

        out_dict = dict()
        out_dict['record_cnt'] = row_count
        record_list = list()
        for row in result:
            row_one = dict()
            row_one['column_comment'] = convertStr(row['column_comment'])
            row_one['column_default'] = convertStr(row['column_default'])

            if row['column_key'] == 'PRI':
                row_one['column_key'] = 1
            else:
                row_one['column_key'] = 0

            row_one['column_name'] = convertStr(row['column_name'])
            row_one['column_type'] = convertStr(row['column_type'])
            row_one['created_by'] = ''
            # 创建时间就是表的创建时间
            row_one['created_tm'] = convertStr(create_tm)
            row_one['updated_by'] = ''
            # 如果metadata里update没有记录，则无
            if row['column_name'] in update_tm.keys():
                row_one['updated_tm'] = convertStr(update_tm[row['column_name']])
            else:
                row_one['updated_tm'] = convertStr('')
            record_list.append(row_one)
        out_dict['record_list'] = record_list

        return self.response_json(data=out_dict)


@route('/table/column_history')
class ColumnHistoryHandler(BaseRequestHandler):

    async def post(self, *args, **kwargs):
        conn_name = self.get_json_data('conn_name')
        table_name = self.get_json_data('table_name')
        column_name = self.get_json_data('column_name')

        # 1:降序 0:升序
        order = self.get_json_data('order')
        strOrder = 'desc'
        if order == 0:
            strOrder = 'asc'

        debug_log('/table/column_history input: {0} {1} {2} {3}'.format(conn_name, table_name, column_name, strOrder))
        if conn_name is None or table_name is None or column_name is None:
            return self.response_json(code=400001)

        db_name = await Db.get_db_name_by_conn(conn_name)
        # 列信息变化
        sql_col_diff = u'''SELECT 
case when a.db_name=b.db_name_dst then '变更前' when a.db_name=b.db_name_src then '变更后' end as '变更状态',
a.sync_cnt,a.job_name,a.db_name,b.db_name_src,b.db_name_dst,
a.table_name,a.column_name,a.column_default,a.is_nullable,a.column_key,a.column_type,a.COLLATION_NAME,a.column_comment,a.table_comment,b.created_tm,b.updated_tm,b.updated_by
FROM db_info a
join column_diff b on(b.job_name=a.job_name and b.sync_cnt=a.sync_cnt and b.table_name = a.table_name and b.column_name=a.column_name)
where 
b.sync_sts=2
and b.db_name_dst = '{0}'
and a.table_name='{1}'
and a.column_name='{2}'
order by b.db_name_dst asc, a.table_name asc,a.COLUMN_NAME asc,a.sync_cnt {3}'''.format(
            db_name + '@' + conn_name, table_name, column_name, strOrder)
        result, row_count = await Db.select(query=sql_col_diff)

        out_dict = dict()
        out_dict['record_cnt'] = row_count
        row_list = list()
        for row in result:
            rowOne = dict()
            rowOne['column_default'] = convertStr(row['column_default'])
            rowOne['column_name'] = convertStr(row['column_name'])
            rowOne['column_type'] = convertStr(row['column_type'])
            rowOne['status'] = convertStr(row[u'变更状态'])
            rowOne['sync_cnt'] = row['sync_cnt']
            rowOne['updated_by'] = convertStr(row['updated_by'])
            rowOne['updated_tm'] = convertStr(row['updated_tm'])
            row_list.append(rowOne)
        out_dict['record_list'] = row_list
        return self.response_json(data=out_dict)
