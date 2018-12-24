# -*- coding: utf-8 -*-

from app.apis.handler_filter import CFilterRequestHandler
from utils.route import route
from app.app import settings
import os


@route('/')
class CIndex(CFilterRequestHandler):
    async def get(self):
        houses = [
            {
                "price": 398,
                "titles": ["宽窄巷子", "160平大空间", "文化保护区双地铁"],
                "score": 5,
                "comments": 6,
                "position": "北京市丰台区六里桥地铁"
            },
            {
                "price": 398,
                "titles": ["宽窄巷子", "160平大空间", "文化保护区双地铁"],
                "score": 5,
                "comments": 6,
                "position": "北京市丰台区六里桥地铁"
            }]
        self.render(os.path.join(settings.get("template_path"), "index.html"), houses=houses,
                    title_join=hourse_title_join)


def hourse_title_join(in_list):
    return "+".join(in_list)
