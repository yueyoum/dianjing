
from dianjing.exception import GameException

from utils.http import ProtobufResponse
from utils.session import GameSession

from apps.account.core import register as register_func
from apps.account.core import regular_login, third_login


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
    req = request._proto.account

    if req.tp == MsgAccount.REGULAR:
        account = regular_login(req.regular.email, req.regular.password)
    elif req.tp == MsgAccount.THIRD:
        account = third_login(req.third.platform, req.third.uid, req.third.param)
    else:
        raise GameException(1)


    response = LoginResponse()
    response.ret = 0
    response.session = GameSession.dumps(account_id=account.account.id)
    response.account.MergeFrom(req)

    return ProtobufResponse(response)


