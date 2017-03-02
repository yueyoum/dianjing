# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       account
Date Created:   2015-07-02 18:23
Description:

"""
from django.conf import settings

from dianjing.exception import GameException

from utils.http import ProtobufResponse
from utils.session import GameSession, LoginID
from utils.push_notification import GeTui

from core.account import register as register_func, regular_login, third_login
from config import ConfigErrorMessage

from protomsg.account_pb2 import RegisterResponse, LoginResponse, GeTuiClientIdResponse


def register(request):
    if not settings.REGISTER_OPEN:
        raise GameException(ConfigErrorMessage.get_error_id("REGISTER_NOT_OPEN"))

    name = request._proto.account.email
    password = request._proto.account.password

    account = register_func(name, password)

    login_id = LoginID.new(account.account.id)

    response = RegisterResponse()
    response.ret = 0
    response.session = GameSession.dumps(account_id=account.account.id, login_id=login_id)
    response.account.MergeFrom(request._proto.account)

    return ProtobufResponse(response)


def login(request):
    if not settings.LOGIN_OPEN:
        raise GameException(ConfigErrorMessage.get_error_id("LOGIN_NOT_OPEN"))

    account = request._proto.account
    provider = account.provider

    if provider in ['debug', 'ios']:
        account = regular_login(account.regular.email, account.regular.password)
    else:
        account = third_login(account.provider, account.third.platform, account.third.uid, account.third.param)

    login_id = LoginID.new(account.account.id)

    response = LoginResponse()
    response.ret = 0
    response.session = GameSession.dumps(account_id=account.account.id, login_id=login_id, provider=provider)
    response.account.MergeFrom(request._proto.account)

    return ProtobufResponse(response)


def set_getui_client_id(request):
    account_id = request._game_session.account_id
    client_id = request._proto.client_id

    if account_id and client_id:
        GeTui(account_id).set_client_id(client_id)

    response = GeTuiClientIdResponse()
    response.ret = 0
    return ProtobufResponse(response)
