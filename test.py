# -*- coding: utf-8 -*-
from utils.db import *


def main():
    import asyncio
    loop = asyncio.get_event_loop()

    db = CDB()

    print(loop.run_until_complete(db.init()))

    res = loop.run_until_complete(db.get_db_info_by_name('local_ods_jff'))
    print(loop.run_until_complete(db.select_one(query='select * from wx_user', args=None,
                                                db_info=res)))

    loop.close()
    print()


if __name__ == '__main__':
    main()
