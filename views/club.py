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
from config import ConfigErrorMessage

from core.signals import game_start_signal
from core.db import get_mongo_db
from core.mongo import Document
from core.club import Club

from protomsg.club_pb2 import (
    CreateClubResponse,
    ClubSetPolicyResponse,
    ClubSetMatchStaffResponse
)



def create(request):
    name = request._proto.name
    flag = request._proto.flag

    session = request._game_session
    server_id = session.server_id
    char_id = session.char_id

    char = Character.objects.get(id=char_id)
    if char.club_name:
        raise GameException( ConfigErrorMessage.get_error_id("CLUB_ALREADY_CREATED") )


    with transaction.atomic():
        try:
            char.club_name = name
            char.save()
        except IntegrityError:
            raise GameException( ConfigErrorMessage.get_error_id("CLUB_NAME_TAKEN") )

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


def set_policy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    policy = request._proto.policy_id

    club = Club(server_id, char_id)
    club.set_policy(policy)

    response = ClubSetPolicyResponse()
    response.ret = 0
    return ProtobufResponse(response)


def set_match_staffs(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    staff_ids = request._proto.staff_ids

    club = Club(server_id, char_id)
    club.set_match_staffs(staff_ids)

    response = ClubSetMatchStaffResponse()
    response.ret = 0
    return ProtobufResponse(response)

