from utils.http import ProtobufResponse
from utils.session import GameSession

from dianjing.exception import GameException
from apps.account.core import register as register_func
from apps.account.core import regular_login, third_login

from protomsg.account_pb2 import RegisterResponse, Account, LoginResponse

def register(request):
    name = request._proto.account.email
    password = request._proto.account.password

    account = register_func(name, password)
    session = GameSession.dumps(account_id=account.account.id)

    response = RegisterResponse()
    response.ret = 0
    response.account.MergeFrom(request._proto.account)

    return ProtobufResponse(response, session=session)


def login(request):
    req = request._proto.account
    if req.tp == Account.REGULAR:
        account = regular_login(req.regular.email, req.regular.password)
    elif req.tp == Account.THIRD:
        account = third_login(req.third.platform, req.third.uid, req.third.param)
    else:
        raise GameException(0, 1)

    session = GameSession.dumps(account_id=account.account.id)

    response = LoginResponse()
    response.ret = 0
    response.account.MergeFrom(req)

    return ProtobufResponse(response, session=session)


