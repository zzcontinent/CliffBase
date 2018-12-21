# -*- coding: utf-8 -*-
import tornado.options
import tornado.httpserver
import tornado.ioloop

from tornado.options import define, options
from dotenv import load_dotenv, find_dotenv

# load environment
load_dotenv(find_dotenv())

from app.app import create_app

define("host", default="0.0.0.0", help="run on the given host", type=str)
define("port", default=9097, help="run on the given port", type=int)


def main():
    tornado.options.parse_command_line()

    application = create_app()

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, options.host)

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
