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

from apps.config.models import Config

from core.db import RedisDB, MongoDB
from utils.http import ProtobufResponse
from utils.session import GameSession, LoginID
from utils.message import NUM_FILED, MessagePipe
from utils.operation_log import OperationLog

from config import ConfigErrorMessage

from protomsg import PATH_TO_REQUEST, PATH_TO_RESPONSE, ID_TO_MESSAGE


class LazyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        RedisDB.connect()
        MongoDB.connect()

        return self.get_response(request)


class VersionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.version = None

    def __call__(self, request):
        if not request.path.startswith('/game/'):
            return self.get_response(request)

        if not self.version:
            self.version = Config.get_config().version

        client_version = request.META.get("HTTP_X_VERSION", "")
        if client_version != self.version:
            print "==== VERSION_NOT_MATCH ===="
            print "SERVER VERSION: {0}, CLIENT VERSION: {1}".format(self.version, client_version)
            error_proto = make_response_with_error_id(request.path,
                                                      ConfigErrorMessage.get_error_id("VERSION_NOT_MATCH"))
            return ProtobufResponse(error_proto)

        return self.get_response(request)


class RequestMiddleware(object):
    # 对所以请求解析protobuf消息，以及session
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/game/'):
            return self.get_response(request)

        if request.method != 'POST':
            return HttpResponse(status=403)

        try:
            session, proto = self.parse_request_message(request.path, request.body)
        except:
            print "==== ERROR ===="
            traceback.print_exc()
            return HttpResponse(status=403)

        request._game_session = session
        request._proto = proto
        if not session.char_id:
            request._operation_log = None
        else:
            request._operation_log = OperationLog(session.server_id, session.char_id)

        print proto
        print session.kwargs

        return self.get_response(request)

    def parse_request_message(self, path, data):
        # 格式：  长度 ID 真实数据
        data = data[8:]  # 去掉 长度 ID

        msg_file, msg_name = PATH_TO_REQUEST[path]
        msg_module = __import__('protomsg.{0}_pb2'.format(msg_file), fromlist=['*'])

        msg = getattr(msg_module, msg_name)

        proto = msg()
        proto.ParseFromString(data)

        if msg_name in ["RegisterRequest", "LoginRequest"]:
            session = GameSession.empty()
        else:
            # 除过上面两个消息，其他消息都应该有session
            session = GameSession.loads(proto.session)
            if msg_name == "SyncRequest":
                if not session.account_id or not session.server_id or not session.char_id:
                    raise Exception("SyncRequest, But session is incomplete")

        return session, proto


class LoginIDMiddleware(object):
    # check login id
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/game/'):
            return self.get_response(request)

        session = request._game_session

        if session.account_id:
            login_id = LoginID.get(session.account_id)
            if not login_id:
                # cache被清空，或者login_id过期
                print "==== RELOGIN ===="
                error_proto = make_response_with_error_id(request.path,
                                                          ConfigErrorMessage.get_error_id("RELOGIN"))
                return ProtobufResponse(error_proto)

            elif session.login_id != login_id:
                print "==== INVALID_LOGIN_ID ===="
                error_proto = make_response_with_error_id(request.path,
                                                          ConfigErrorMessage.get_error_id("INVALID_LOGIN_ID"))
                return ProtobufResponse(error_proto)

            LoginID.update_expire(session.account_id)

        return self.get_response(request)


class ResponseMiddleware(object):
    # 在这里将队列中的消息一起取出返回给客户端
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/game/'):
            return self.get_response(request)

        request._game_error_id = 0
        response = self.get_response(request)

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
        # _msg_names = []
        # for _msg in all_msgs:
        #     _msg_id = NUM_FILED.unpack(_msg[4:8])[0]
        #     _msg_names.append(ID_TO_MESSAGE[_msg_id])
        #
        # print _msg_names
        # END DEBUG

        return HttpResponse(''.join(all_msgs), content_type='text/plain')


class ExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if not isinstance(exception, GameException):
            return None

        request._game_error_id = exception.error_id
        char_id = request._game_session.char_id

        print "==== WARNING ===="
        print "Char: {0}, Error: {1}, {2}".format(char_id, exception.error_id, exception.error_msg)

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
