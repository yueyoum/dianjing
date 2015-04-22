
from django.db import IntegrityError
from dianjing.exception import GameException
from apps.character.models import Character
from apps.club.models import Club

from utils.http import ProtobufResponse
from utils.session import GameSession

from protomsg.club_pb2 import CreateClubResponse

def create(request):
    req = request._proto

    name = req.name
    flag = req.flag

    session = GameSession.loads(req.session)

    server_id = session.server_id
    char_id = session.char_id

    if Club.objects.filter(char_id=char_id).exists():
        raise GameException(char_id, 3)

    char_name = Character.objects.get(id=char_id).name

    try:
        club = Club.objects.create(
            char_id=char_id,
            char_name=char_name,
            server_id=server_id,
            name=name,
            flag=flag
        )
    except IntegrityError as e:
        print "===="
        print e
        raise GameException(char_id, 4)

    session_kwargs = session.kwargs
    session_kwargs['club_id'] = club.id

    session = GameSession.dumps(session_kwargs)

    response = CreateClubResponse()
    response.ret = 0
    return ProtobufResponse(response, session=session)
