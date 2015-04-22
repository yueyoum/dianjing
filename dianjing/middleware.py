# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       middleware
Date Created:   2015-04-22 14:02
Description:

"""

import traceback

from django.http import HttpResponse

from dianjing.exception import GameException
from utils.http import ProtobufResponse

from protomsg import PATH_TO_REQUEST, PATH_TO_RESPONSE

class GameRequestMiddleware(object):
    def process_request(self, request):
        if not request.path.startswith('/game/'):
            return

        if request.method != 'POST':
            return HttpResponse(status=403)

        try:
            data = request.body[4:]
            msg_file, msg_name = PATH_TO_REQUEST[request.path]
            msg_module = __import__('protomsg.{0}_pb2'.format(msg_file), fromlist=['*'])

            msg = getattr(msg_module, msg_name)

            proto = msg()
            proto.ParseFromString(data)
        except:
            print "==== ERROR ===="
            traceback.print_exc()
            return HttpResponse(status=403)

        request._proto = proto


class GameExceptionMiddleware(object):
    def process_exception(self, request, exception):
        if not request.path.startswith("/game/"):
            return

        if not isinstance(exception, GameException):
            return

        msg_file, msg_name = PATH_TO_RESPONSE[request.path]
        msg_module = __import__('protomsg.{0}_pb2'.format(msg_file), fromlist=['*'])

        msg = getattr(msg_module, msg_name)

        proto = msg()
        proto.ret = exception.error_id

        return ProtobufResponse(proto)

