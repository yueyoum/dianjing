# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       account
Date Created:   2015-07-02 18:23
Description:

"""


from dianjing.exception import GameException

from utils.http import ProtobufResponse
from utils.session import GameSession

from core.account import register as register_func, regular_login, third_login

from protomsg.account_pb2 import Account as MsgAccount, RegisterResponse, LoginResponse


def register(request):
    name = request._proto.account.email
    password = request._proto.account.password

    account = register_func(name, password)

    response = RegisterResponse()
    response.ret = 0
    response.session = GameSession.dumps(account_id=account.account.id)
    response.account.MergeFrom(request._proto.account)

    return ProtobufResponse(response)


def login(request):
    account = request._proto.account

    if account.tp == MsgAccount.REGULAR:
        account = regular_login(account.regular.email, account.regular.password)
    elif account.tp == MsgAccount.THIRD:
        account = third_login(account.third.platform, account.third.uid, account.third.param)
    else:
        raise GameException(1)


    response = LoginResponse()
    response.ret = 0
    response.session = GameSession.dumps(account_id=account.account.id)
    response.account.MergeFrom(request._proto.account)

    return ProtobufResponse(response)


