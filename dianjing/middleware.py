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

from core.db import RedisDB, MongoDB
from utils.http import ProtobufResponse
from utils.session import GameSession, LoginID
from utils.message import NUM_FILED, MessagePipe
from utils.operation_log import OperationLog

from config import ConfigErrorMessage

from protomsg import PATH_TO_REQUEST, PATH_TO_RESPONSE, ID_TO_MESSAGE


class GameLazyInitializeMiddleware(object):
    def process_request(self, request):
        RedisDB.connect()
        MongoDB.connect()


class GameRequestMiddleware(object):
    # 对所以请求解析protobuf消息，以及session
    def process_request(self, request):
        if not request.path.startswith('/game/'):
            return

        if request.method != 'POST':
            return HttpResponse(status=403)

        # NOTE
        request._operation_log = None
        request._game_error_id = 0

        session = GameSession.empty()
        request._game_session = session

        try:
            # body 格式：  数量 ID 长度 真实数据
            data = request.body[12:]  # 去掉 数量 ID 长度
            msg_file, msg_name = PATH_TO_REQUEST[request.path]
            msg_module = __import__('protomsg.{0}_pb2'.format(msg_file), fromlist=['*'])

            msg = getattr(msg_module, msg_name)

            proto = msg()
            proto.ParseFromString(data)

            # NOTE
            request._proto = proto

            if msg_name not in ["RegisterRequest", "LoginRequest"]:
                # 除过这两个消息，其他消息都应该有session
                session = GameSession.loads(proto.session)
                request._game_session = session

                login_id = LoginID.get(session.account_id)
                error_id = 0
                if not login_id:
                    # cache被清空，或者login_id过期
                    if not session.login_id:
                        error_id = ConfigErrorMessage.get_error_id("BAD_MESSAGE")
                    else:
                        LoginID.new(session.account_id, value=session.login_id)

                elif session.login_id != login_id:
                    error_id = ConfigErrorMessage.get_error_id("INVALID_LOGIN_ID")

                if error_id:
                    # 这里还要走一遍 GameResponseMiddleware
                    # 为了不让这个请求把 正常的通知带走，这里得把 char_id 清空
                    request._game_session.char_id = None
                    error_proto = make_response_with_error_id(request.path, error_id)
                    return ProtobufResponse(error_proto)

                if session.char_id:
                    request._operation_log = OperationLog(session.server_id, session.char_id)
        except:
            print "==== ERROR ===="
            traceback.print_exc()
            return HttpResponse(status=403)

        print proto
        print session.kwargs


class GameResponseMiddleware(object):
    # 在这里将队列中的消息一起取出返回给客户端
    def process_response(self, request, response):
        if not request.path.startswith('/game/'):
            return response

        if response.status_code != 200:
            return response

        if request._operation_log:
            request._operation_log.record(request.path, request._game_error_id)
            request._operation_log = None

        char_id = request._game_session.char_id
        if char_id:
            all_msgs = MessagePipe(char_id).get()
        else:
            all_msgs = []

        all_msgs.insert(0, response.content)

        # FOR DEBUG
        _msg_names = []
        for _msg in all_msgs:
            _msg_id = NUM_FILED.unpack(_msg[:4])[0]
            _msg_names.append(ID_TO_MESSAGE[_msg_id])

        print _msg_names
        # END DEBUG

        num_of_msgs = len(all_msgs)

        result = '%s%s' % (
            NUM_FILED.pack(num_of_msgs),
            ''.join(all_msgs)
        )

        return HttpResponse(result, content_type='text/plain')


class GameExceptionMiddleware(object):
    # 统一的错误处理
    def process_exception(self, request, exception):
        if not request.path.startswith("/game/"):
            return

        if not isinstance(exception, GameException):
            return

        char_id = request._game_session.char_id

        print "==== WARNING ===="
        print "Char: {0}, Error: {1}, {2}".format(char_id, exception.error_id, exception.error_msg)

        request._game_error_id = exception.error_id

        proto = make_response_with_error_id(request.path, exception.error_id)
        return ProtobufResponse(proto)


def make_response_with_error_id(request_path, error_id):
    msg_file, msg_name = PATH_TO_RESPONSE[request_path]
    msg_module = __import__('protomsg.{0}_pb2'.format(msg_file), fromlist=['*'])

    msg = getattr(msg_module, msg_name)

    proto = msg()
    proto.ret = error_id
    proto.session = ""

    return proto
