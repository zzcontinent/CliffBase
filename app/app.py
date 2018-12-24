# -*- coding: utf-8 -*-
import os
import re
from utils.log import init_log, debug_log
from utils.route import route
import importlib
import tornado.web

settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "statics")
)


def __import_module(dir_path):
    module_list = re.split('[./]', dir_path)
    module_list = [x for x in module_list if x]
    module_path = '.'.join(module_list)
    debug_log('module_path %s', module_path)
    file_list = os.listdir(dir_path)
    for f in file_list:
        if f.endswith('.py') and f != '__init__.py':
            module_name = module_path + '.' + os.path.splitext(f)[0]
            debug_log('module_name %s', module_name)
            importlib.import_module(module_name)


def create_app():
    init_log()
    __import_module('./app/apis')
    app = tornado.web.Application(route.urls, **settings)
    return app
