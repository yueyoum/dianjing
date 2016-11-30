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

from core.account import register as register_func, regular_login, third_login
from config import ConfigErrorMessage

from protomsg.account_pb2 import Account as MsgAccount, RegisterResponse, LoginResponse


def register(request):
    if not settings.REGISTER_OPEN:
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

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
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    account = request._proto.account

    if account.tp == MsgAccount.REGULAR:
        account = regular_login(account.regular.email, account.regular.password)
    elif account.tp == MsgAccount.THIRD:
        account = third_login(account.third.platform, account.third.uid, account.third.param)
    else:
        raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

    login_id = LoginID.new(account.account.id)

    response = LoginResponse()
    response.ret = 0
    response.session = GameSession.dumps(account_id=account.account.id, login_id=login_id)
    response.account.MergeFrom(request._proto.account)

    return ProtobufResponse(response)
