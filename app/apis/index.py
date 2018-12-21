# -*- coding: utf-8 -*-

from app.apis.filter_request_handler import CFilterRequestHandler
from app.route import route

TemplatesDir = 'app/templates/'


@route('/')
class CIndex(CFilterRequestHandler):
    async def get(self):
        with open(TemplatesDir + 'index.html', 'r') as fd:
            self.write(fd.read())
