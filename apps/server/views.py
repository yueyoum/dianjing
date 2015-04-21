
import arrow

from utils.http import ProtobufResponse
from protomsg.server_pb2 import GetServerListResponse

from apps.server.models import Server

def get_server_list(request):
    now = arrow.utcnow().format("YYYY-MM-DD HH:mm:ss")

    servers = Server.objects.filter(open_at__gte=now)
    response = GetServerListResponse()
    response.ret = 0
    for server in servers:
        s = response.servers.add()
        s.id = server.id
        s.name = server.name
        s.status = server.status

    return ProtobufResponse(response)

