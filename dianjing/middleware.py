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
from utils.session import GameSession
from utils.http import NUM_FILED

from protomsg import PATH_TO_REQUEST, PATH_TO_RESPONSE


class GameRequestMiddleware(object):
    # 对所以请求解析protobuf消息，以及session
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

            session = proto.session
            if msg_name not in ["RegisterRequest", "LoginRequest"]:
                # 其他消息都应该有session
                session = GameSession.loads(session)

        except:
            print "==== ERROR ===="
            traceback.print_exc()
            return HttpResponse(status=403)

        request._proto = proto
        request._game_session = session



class GameResponseMiddleware(object):
    # 在这里将队列中的消息一起取出返回给客户端
    def process_response(self, request, response):
        if not request.path.startswith('/game/'):
            return response

        if response.status_code != 200:
            return response

        try:
            char_id = request._game_session.char_id
        except:
            char_id = None


        # XXX
        if char_id:
            other_msgs = []
        else:
            other_msgs = []


        num_of_msgs = len(other_msgs) + 1

        result = '%s%s%s' % (
            NUM_FILED.pack(num_of_msgs),
            response.content,
            ''.join(other_msgs)
        )

        return HttpResponse(result, content_type='text/plain')



class GameExceptionMiddleware(object):
    # 统一的错误处理
    def process_exception(self, request, exception):
        if not request.path.startswith("/game/"):
            return

        if not isinstance(exception, GameException):
            return

        try:
            char_id = request._game_session.char_id
        except:
            char_id = None
        print "==== WARNING ===="
        print "Char: {0}, Error: {1}, {2}".format(char_id, exception.error_id, exception.error_msg)

        msg_file, msg_name = PATH_TO_RESPONSE[request.path]
        msg_module = __import__('protomsg.{0}_pb2'.format(msg_file), fromlist=['*'])

        msg = getattr(msg_module, msg_name)

        proto = msg()
        proto.ret = exception.error_id

        return ProtobufResponse(proto)

