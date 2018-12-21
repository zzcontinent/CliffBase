# -*- coding: utf-8 -*-
import aiomysql
import asyncio
from utils.enc_dec import dec, enc
from sshtunnel import SSHTunnelForwarder
from utils.log import debug_log, error_log, info_log
import pandas as pd


# 连接数据库配置信息
class CDBBaseInfo:
    def __init__(self):
        # db_config连接信息
        self.m_conn_type = 0
        self.m_conn_pk_name = 'db_config'
        self.m_db_host = '127.0.0.1'
        self.m_db_port = 3306
        self.m_db_user = 'root'
        self.m_db_passwd = '123456'
        self.m_db_name = 'metadata'
        self.m_charset = 'utf8mb4'
        self.m_db_pool_minsize = 1
        self.m_db_pool_maxsize = 50
        self.m_db_connect_timeout = 5
        self.m_pool_recycle = 6 * 60 * 60
        # 是否需要ssh
        self.m_ssh_need = 0
        self.m_ssh_host = ''
        self.m_ssh_user = ''
        self.m_ssh_port = 0
        self.m_ssh_passwd = ''


_DBBaseInfo = CDBBaseInfo()


class CDB:
    def __init__(self, db_base_info=_DBBaseInfo):
        self.m_db_pool = {}
        self.m_db_conn_name_dict = {}
        self.m_sshtunnel = dict()
        self.m_df_db_config = pd.DataFrame()
        self.m_db_base_info = db_base_info
        asyncio.get_event_loop().run_until_complete(self._init_df_db_config())

    async def _init_df_db_config(self):
        query = 'select * from db_config where is_enabled = 1 and is_display=1'
        base_db_pool = await self._create_db_pool()
        async with base_db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                result = await cursor.fetchall()
                for row in result:
                    self.m_df_db_config = self.m_df_db_config.append(
                        {'db_config_id': row['db_config_id'],
                         'conn_name': row['conn_name'],
                         'user': row['user'],
                         'passwd': row['passwd'],
                         'host': row['host'],
                         'port': row['port'],
                         'db_name': row['db_name'],
                         'ssh_sts': row['ssh_sts'],
                         'ssh_sk': row['ssh_sk'],
                         'charset': row['charset']},
                        ignore_index=True)

    def close_conn(self):
        for k in self.m_db_pool.keys():
            self.m_db_pool[k].close()
        for k in self.m_sshtunnel.keys():
            self.m_sshtunnel[k].stop()
            self.m_db_conn_name_dict = dict()
            self.m_db_pool = dict()
            self.m_sshtunnel = dict()
        debug_log('close_conn' + '*' * 20)

    def get_db_info_by_name(self, conn_name):
        if conn_name == self.m_db_base_info.m_conn_pk_name:
            return self.m_db_base_info
        else:
            df_one = self.m_df_db_config[self.m_df_db_config['conn_name'] == conn_name]
            db_info = CDBBaseInfo()
            if len(df_one) > 0:
                for _, row in df_one.iterrows():
                    db_info.m_conn_pk_name = row['conn_name']
                    db_info.m_charset = row['charset']
                    db_info.m_db_host = row['host']
                    db_info.m_db_port = row['port']
                    db_info.m_db_user = row['user']
                    db_info.m_db_name = row['db_name']
                    db_info.m_db_passwd = dec(row['passwd'])
                    if int(row['ssh_sts']) > 0:
                        df_ssh = self.m_df_db_config[self.m_df_db_config['db_config_id'] == row['ssh_sk']]
                        for row_ssh in df_ssh:
                            db_info.m_ssh_user = row_ssh['user']
                            db_info.m_ssh_host = row_ssh['host']
                            db_info.m_ssh_port = row_ssh['port']
                            db_info.m_ssh_passwd = dec(row_ssh['passwd'])
                            db_info.m_ssh_need = 1
                    return db_info
            else:
                error_log('no connect name ' + conn_name)
                return None

    async def _create_db_pool(self, db_info=None, loop=None):
        if db_info is None:
            db_info = self.m_db_base_info
        if db_info.m_conn_pk_name not in self.m_db_pool:
            # 如果是数据库连接  不需要ssh
            if db_info.m_ssh_need == 0:
                self.m_db_pool[db_info.m_conn_pk_name] = await aiomysql.create_pool(
                    host=db_info.m_db_host,
                    port=int(db_info.m_db_port),
                    user=db_info.m_db_user,
                    password=db_info.m_db_passwd,
                    db=db_info.m_db_name,
                    charset=db_info.m_charset,
                    cursorclass=aiomysql.DictCursor,
                    autocommit=True,
                    minsize=db_info.m_db_pool_minsize,
                    maxsize=db_info.m_db_pool_maxsize,
                    connect_timeout=db_info.m_db_connect_timeout,
                    loop=loop,
                    pool_recycle=db_info.m_pool_recycle
                )
                debug_log(u'新增连接' + '*' * 20)
                debug_log(db_info.m_conn_pk_name)
            elif db_info.m_ssh_need == 1:
                ssh_conn_pk_name = db_info.m_ssh_host + ':' + str(db_info.m_ssh_port)
                if ssh_conn_pk_name not in self.m_sshtunnel:
                    server = SSHTunnelForwarder(
                        (db_info.m_ssh_host, int(db_info.m_ssh_port)),  # ssh机的配置
                        ssh_password=db_info.m_ssh_passwd,
                        ssh_username=db_info.m_ssh_user,
                        remote_bind_address=(db_info.m_db_host, int(db_info.m_db_port)))  # 目标机的配置
                    # 开启ssh端口映射通道
                    server.start()
                    self.m_sshtunnel[ssh_conn_pk_name] = server
                    debug_log(u'新增ssh tunnel' + '*' * 20)
                    debug_log(ssh_conn_pk_name)

                # 创建带ssh的连接
                self.m_db_pool[db_info.m_conn_pk_name] = await aiomysql.create_pool(
                    host=self.m_sshtunnel[ssh_conn_pk_name].local_bind_host,
                    port=self.m_sshtunnel[ssh_conn_pk_name].local_bind_port,
                    user=db_info.m_db_user,
                    password=db_info.m_db_passwd,
                    db=db_info.m_db_name,
                    charset=db_info.m_charset,
                    cursorclass=aiomysql.DictCursor,
                    autocommit=True,
                    minsize=db_info.m_db_pool_minsize,
                    maxsize=db_info.m_db_pool_maxsize,
                    connect_timeout=db_info.m_db_connect_timeout,
                    loop=loop,
                    pool_recycle=db_info.m_pool_recycle
                )
                debug_log(u'新增连接' + '*' * 20)
                debug_log(db_info.m_conn_pk_name)

        return self.m_db_pool[db_info.m_conn_pk_name]

    async def select(self, query, args=None, size=None, db_info=None):
        if db_info is None:
            db_info = self.m_db_base_info
        pool = await self._create_db_pool(db_info)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, args)
                if size is None:
                    result = await cursor.fetchall()
                else:
                    result = await cursor.fetchmany(size)
                rowcount = cursor.rowcount
                return result, rowcount

    async def select_one(self, query, args=None, db_info=None):
        if db_info is None:
            db_info = self.m_db_base_info
        pool = await self._create_db_pool(db_info)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, args)
                result = await cursor.fetchone()
                rowcount = cursor.rowcount
                return result, rowcount

    async def insert(self, query, args=None, db_info=None):
        if db_info is None:
            db_info = self.m_db_base_info
        pool = await self._create_db_pool(db_info)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, args)
            return cursor.rowcount, cursor.lastrowid

    async def insert_many(self, query, args=None, db_info=None):
        if db_info is None:
            db_info = self.m_db_base_info
        pool = await self._create_db_pool(db_info)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.executemany(query, args)
            return cursor.rowcount

    async def update(self, query, args=None, db_info=None):
        if db_info is None:
            db_info = self.m_db_base_info
        pool = await self._create_db_pool(db_info)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, args)
                affected_rows = cursor.rowcount
            return affected_rows

    async def execute_many(self, query_list, args_list, db_info=None):
        if db_info is None:
            db_info = self.m_db_base_info
        pool = await self._create_db_pool(db_info)
        async with pool.acquire() as conn:
            i = 0
            async with conn.cursor() as cursor:
                for query, args in zip(query_list, args_list):
                    await cursor.execute(query, args)
                    i += 1
                affected_rows = cursor.rowcounts
            return affected_rows


GloabalDB = CDB()
