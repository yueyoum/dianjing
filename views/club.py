# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-08 15:12
Description:

"""


from django.db import IntegrityError
from django.db import transaction

from dianjing.exception import GameException
from apps.character.models import Character

from utils.http import ProtobufResponse
from config import CONFIG

from protomsg.club_pb2 import CreateClubResponse

from core.signals import game_start_signal
from core.db import get_mongo_db
from core.mongo import Document

def create(request):
    name = request._proto.name
    flag = request._proto.flag

    session = request._game_session
    server_id = session.server_id
    char_id = session.char_id

    char = Character.objects.get(id=char_id)
    if char.club_name:
        raise GameException( CONFIG.ERRORMSG["CLUB_ALREADY_CREATED"].id )


    with transaction.atomic():
        try:
            char.club_name = name
            char.save()
        except IntegrityError:
            raise GameException( CONFIG.ERRORMSG["CLUB_NAME_TAKEN"].id )

        doc = Document.get("character")
        doc['_id'] = char_id
        doc['name'] = char.name
        doc['club']['name'] = name
        doc['club']['flag'] = flag

        mongo = get_mongo_db(server_id)
        mongo.character.insert_one(doc)


    game_start_signal.send(
        sender=None,
        server_id=server_id,
        char_id=char_id,
    )

    response = CreateClubResponse()
    response.ret = 0
    response.session = session.serialize()
    return ProtobufResponse(response)
