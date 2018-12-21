# -*- coding: utf-8 -*-
import os
import re
from utils.config import config
from .log import init_log, debug_log
from .route import route
import importlib
import tornado.web


def __import_module(dir_path):
    module_list = re.split('[./]', dir_path)
    module_list = [x for x in module_list if x]
    module_path = '.'.join(module_list)
    debug_log(module_path)
    file_list = os.listdir(dir_path)
    for f in file_list:
        if f.endswith('.py') and f != '__init__.py':
            module_name = module_path + '.' + os.path.splitext(f)[0]
            debug_log(module_name)
            importlib.import_module(module_name)


def create_app():
    init_log(config.log_path, config.log_level)

    # handlers = [
    #     ("/user/([0-9]+)", UserHandler),
    #     ("/auth/login", AuthLoginHandler),
    # ]
    #
    # app = tornado.web.Application(handlers, **settings)
    __import_module('./app/api_1_0')
    print(route.urls)
    app = tornado.web.Application(route.urls)

    return app
