# -*- coding: utf-8 -*-
import aiomysql
from utils.config import config
from utils.enc_dec import dec
from app.exceptions import *
from sshtunnel import SSHTunnelForwarder
import threading
from utils.log import debug_log, error_log, info_log

default_db_conn_name = '_default_mysql_db_conn__'


class Db:
    """Db sql execute using aiomysql pool."""
    __db_pool = {}
    __db_conn_name_dict = {}
    __sshtunnel = dict()
    __pool_recycle = 60 * 60 * 1

    @staticmethod
    def close_conn():
        debug_log('close_conn' + '*' * 20)
        debug_log(Db.__db_conn_name_dict)
        debug_log(Db.__db_pool)
        debug_log(Db.__sshtunnel)

        for k in Db.__db_pool.keys():
            Db.__db_pool[k].close()

        for k in Db.__sshtunnel.keys():
            Db.__sshtunnel[k].stop()

        Db.__db_conn_name_dict = dict()
        Db.__db_pool = dict()
        Db.__sshtunnel = dict()

    @staticmethod
    async def create_db_pool(db_conn_name=default_db_conn_name, loop=None):
        if db_conn_name in Db.__db_pool:
            return Db.__db_pool[db_conn_name]

        if db_conn_name == default_db_conn_name:
            if config.ssh_need != 1:
                Db.__db_pool[db_conn_name] = await aiomysql.create_pool(
                    host=config.db_host,
                    port=config.db_port,
                    user=config.db_user,
                    password=dec(config.db_password),
                    db=config.db_schema,
                    charset='utf8mb4',
                    cursorclass=aiomysql.DictCursor,
                    autocommit=False,
                    minsize=config.db_pool_minsize,
                    maxsize=config.db_pool_maxsize,
                    connect_timeout=config.db_connect_timeout,
                    loop=loop,
                    # pool_recycle=Db.__pool_recycle
                )
                debug_log(u'新增连接' + '*' * 20)
                debug_log(db_conn_name)
            elif config.ssh_need == 1:
                ssh_conn_name = config.ssh_host + ':' + str(config.ssh_port)
                if ssh_conn_name not in Db.__sshtunnel:
                    server = SSHTunnelForwarder(
                        (config.ssh_host, int(config.ssh_port)),  # ssh机的配置
                        ssh_password=dec(config.ssh_passwd),
                        ssh_username=config.ssh_user,
                        remote_bind_address=(config.db_host, int(config.db_port)))  # 目标机的配置
                    # 开启ssh端口映射通道
                    server.start()
                    Db.__sshtunnel[ssh_conn_name] = server
                    debug_log('新增ssh tunnel' + '*' * 20)
                    debug_log(ssh_conn_name, server)
                Db.__db_pool[db_conn_name] = await aiomysql.create_pool(
                    host='127.0.0.1',
                    port=Db.__sshtunnel[ssh_conn_name].local_bind_port,
                    user=config.db_user,
                    password=dec(config.db_password),
                    db=config.db_schema,
                    charset='utf8mb4',
                    cursorclass=aiomysql.DictCursor,
                    autocommit=False,
                    minsize=config.db_pool_minsize,
                    maxsize=config.db_pool_maxsize,
                    connect_timeout=config.db_connect_timeout,
                    loop=loop,
                    # pool_recycle=Db.__pool_recycle
                )
                debug_log(u'新增连接' + '*' * 20)
                debug_log(db_conn_name)
        else:
            row, _ = await Db.select_one(
                '''SELECT * FROM `db_config` where is_enabled=1 and conn_name ='{0}' and is_display=1 '''.format(
                    db_conn_name))
            if not row:
                raise NoDBConnectConfigException

            conn_type = row['conn_type']
            ssh_sts = row['ssh_sts']
            ssh_sk = row['ssh_sk']
            env = row['env']
            conn_name = row['conn_name']
            user = row['user']
            passwd = dec(row['passwd'])
            host = row['host']
            port = int(row['port'])
            db_name = row['db_name']
            charset = row['charset']

            # 如果是数据库连接  不需要ssh
            if conn_type == 0 and ssh_sts == 0:
                Db.__db_pool[db_conn_name] = await aiomysql.create_pool(
                    host=row['host'],
                    port=int(row['port']),
                    user=row['user'],
                    password=dec(row['passwd']),
                    db=row['db_name'],
                    charset='utf8mb4',
                    cursorclass=aiomysql.DictCursor,
                    autocommit=False,
                    minsize=config.db_pool_minsize,
                    maxsize=config.db_pool_maxsize,
                    connect_timeout=config.db_connect_timeout,
                    loop=loop,
                    # pool_recycle=Db.__pool_recycle
                )
                debug_log(u'新增连接' + '*' * 20)
                debug_log(db_conn_name)
            elif conn_type == 0 and ssh_sts == 1:
                rowSSh, _ = await Db.select_one(
                    '''SELECT * FROM `db_config` where is_enabled=1 and db_config_id={0} '''.format(ssh_sk))

                ssh_conn_name = rowSSh['host'] + ':' + str(rowSSh['port'])
                if ssh_conn_name not in Db.__sshtunnel:
                    server = SSHTunnelForwarder(
                        (rowSSh['host'], int(rowSSh['port'])),  # ssh机的配置
                        ssh_password=dec(rowSSh['passwd']),
                        ssh_username=rowSSh['user'],
                        remote_bind_address=(row['host'], int(row['port'])))  # 目标机的配置
                    # 开启ssh端口映射通道
                    server.start()
                    Db.__sshtunnel[ssh_conn_name] = server
                    debug_log(u'新增ssh tunnel' + '*' * 20)
                    debug_log(ssh_conn_name, server)
                Db.__db_pool[db_conn_name] = await aiomysql.create_pool(
                    host='127.0.0.1',
                    port=Db.__sshtunnel[ssh_conn_name].local_bind_port,
                    user=user,
                    password=dec(row['passwd']),
                    db=db_name,
                    charset='utf8mb4',
                    cursorclass=aiomysql.DictCursor,
                    autocommit=False,
                    minsize=config.db_pool_minsize,
                    maxsize=config.db_pool_maxsize,
                    connect_timeout=config.db_connect_timeout,
                    loop=loop,
                    # pool_recycle=Db.__pool_recycle
                )
                debug_log(u'新增连接' + '*' * 20)
                debug_log(db_conn_name)

        return Db.__db_pool[db_conn_name]

    @staticmethod
    async def get_db_pool(db_conn_name=default_db_conn_name):
        if db_conn_name not in Db.__db_pool:
            return await Db.create_db_pool(db_conn_name)
        else:
            return Db.__db_pool[db_conn_name]

    @staticmethod
    async def get_db_name_by_conn(db_conn_name):
        if not db_conn_name:
            return ''

        if db_conn_name in Db.__db_conn_name_dict:
            return Db.__db_conn_name_dict[db_conn_name]

        row, _ = await Db.select_one(
            "select db_name from db_config "
            "where conn_name=%s and conn_type=0 and is_enabled=1 and is_display=1",
            db_conn_name
        )
        if not row:
            raise NoDBConnectConfigException

        Db.__db_conn_name_dict[db_conn_name] = row['db_name']
        return Db.__db_conn_name_dict[db_conn_name]

    @staticmethod
    async def select(query, args=None, size=None, db_conn_name=default_db_conn_name):
        """Executes the given select operation

        Executes the given select operation substituting any markers with
        the given parameters.

        For example, getting all rows where id is 5:
          Db.select("SELECT * FROM t1 WHERE id = %s", (5,))

        :param query: ``str`` sql statement
        :param args: ``tuple`` or ``list`` of arguments for sql query
        :param size: ``int`` or None, size rows returned
        :param db_conn_name: ``str`` db conn name
        :returns: ``list``
        """
        try:
            pool = await Db.get_db_pool(db_conn_name)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, args)
                    if size is None:
                        result = await cursor.fetchall()
                    else:
                        result = await cursor.fetchmany(size)
                    rowcount = cursor.rowcount
                    return result, rowcount
        except Exception as e:
            if e.args[0] == 2003:
                raise DBConnFaild
            elif type(args) is list:
                args = tuple(args)
                error_log("db select errror [%s]: %s", query % args, e)
                raise

    @staticmethod
    async def select_one(query, args=None, db_conn_name=default_db_conn_name):
        """Executes the given select operation, but only fetch one row.

        Executes the given select operation substituting any markers with
        the given parameters.

        For example, getting one row where id is 5:
          Db.select_one("SELECT * FROM t1 WHERE id = %s limit 1", (5,))

        :param query: ``str`` sql statement
        :param args: ``tuple`` or ``list`` of arguments for sql query
        :param db_conn_name: ``str`` db conn name
        :returns: ``dict``
        """
        try:
            pool = await Db.get_db_pool(db_conn_name)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, args)
                    result = await cursor.fetchone()
                    rowcount = cursor.rowcount
                    return result, rowcount
        except Exception as e:
            if e.args[0] == 2003:
                raise DBConnFaild
            if type(args) is list:
                args = tuple(args)
                error_log("db select one errror [%s]: %s", query % args, e)
                raise

    @staticmethod
    async def insert(query, args=None, db_conn_name=default_db_conn_name):
        """Executes the given insert operation

        Executes the given insert operation substituting any markers with
        the given parameters.

        For example, insert table t1 one row:
          Db.insert("insert into t1(id, name) values (%s, %s)", (5, 'Jack'))

        :param query: ``str`` sql statement
        :param args: ``tuple`` or ``list`` of arguments for sql query
        :param db_conn_name: ``str`` db conn name
        :returns: ``int``, number of rows that has been produced of affected
        """
        pool = await Db.get_db_pool(db_conn_name)
        async with pool.acquire() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, args)
                    affected_rows = cursor.rowcount
                    lastrowid = cursor.lastrowid
                await conn.commit()
                return affected_rows, lastrowid
            except Exception as e:
                await conn.rollback()
                if e.args[0] == 2003:
                    raise DBConnFaild
                if type(args) is list:
                    args = tuple(args)
                error_log("db insert errror [%s]: %s", query % args, e)
                raise

    @staticmethod
    async def insert_many(query, args=None, db_conn_name=default_db_conn_name):
        """Executes the given insert operation

        Executes the given insert operation substituting any markers with
        the given parameters.

        For example, insert table t1 many rows:
          Db.insert_many("insert into t1(id, name) values (%s, %s)", [(5, 'Jack'), (6,'Tom')])

        :param query: ``str`` sql statement
        :param args: ``tuple`` or ``list`` of arguments for sql query
        :param db_conn_name: ``str`` db conn name
        :returns: ``int``, number of rows that has been produced of affected
        """
        pool = await Db.get_db_pool(db_conn_name)
        async with pool.acquire() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.executemany(query, args)
                    affected_rows = cursor.rowcount
                await conn.commit()
                return affected_rows
            except Exception as e:
                await conn.rollback()
                if e.args[0] == 2003:
                    raise DBConnFaild
                else:
                    error_log("db insert many errror [%s]: %s", query % list(args), e)
                    raise

    @staticmethod
    async def update(query, args=None, db_conn_name=default_db_conn_name):
        """Executes the given update operation

        Executes the given update operation substituting any markers with
        the given parameters.

        For example, update table t1 where id is 5:
          Db.update("update t1 set name=%s where id=%s", ('Jack', 5))

        :param query: ``str`` sql statement
        :param args: ``tuple`` or ``list`` of arguments for sql query
        :param db_conn_name: ``str`` db conn name
        :returns: ``int``, number of rows that has been produced of affected
        """
        pool = await Db.get_db_pool(db_conn_name)
        async with pool.acquire() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, args)
                    affected_rows = cursor.rowcount
                await conn.commit()
                return affected_rows
            except Exception as e:
                await conn.rollback()
                if e.args[0] == 2003:
                    raise DBConnFaild
                if type(args) is list:
                    args = tuple(args)
                    error_log("db update errror [%s]: %s", query % args, e)
                    raise

    @staticmethod
    async def execute_many(query_list, args_list, db_conn_name=default_db_conn_name):
        """Executes the given dml operations

        Executes the given dml operations substituting any markers with
        the given parameters.

        For example, insert table t1 many rows:
          Db.insert_many("insert into t1(id, name) values (%s, %s)", [(5, 'Jack'), (6,'Tom')])

        :param query_list: ``list`` sql statement list
        :param args_list: ``list`` of arguments for sql query
        :param db_conn_name: ``str`` db conn name
        :returns: ``int``, number of rows that has been produced of affected
        """
        pool = await Db.get_db_pool(db_conn_name)
        async with pool.acquire() as conn:
            i = 0
            try:
                async with conn.cursor() as cursor:
                    for query, args in zip(query_list, args_list):
                        await cursor.execute(query, args)
                        i += 1
                    affected_rows = cursor.rowcount
                await conn.commit()
                return affected_rows
            except Exception as e:
                await conn.rollback()
                if e.args[0] == 2003:
                    raise DBConnFaild
                error_log("db execute many errror [%s]: %s", query_list[i] % list(args_list[i]), e)
                raise

    @staticmethod
    def time_task():
        Db.close_conn()
        timer = threading.Timer(60 * 60 * 5.5, Db.time_task)
        timer.start()


# 5.5h 清空连接
Db.time_task()
