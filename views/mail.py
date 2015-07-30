# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mail
Date Created:   2015-07-30 16:54
Description:

"""

from utils.http import ProtobufResponse

from core.mail import MailManager

from protomsg.mail_pb2 import (
    MailSendResponse,
    MailOpenResponse,
    MailDeleteResponse,
    MailGetAttachmentResponse,
)


def send(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    to_id = request._proto.to_id
    content = request._proto.content

    m = MailManager(server_id, char_id)
    m.send(to_id, content)

    response = MailSendResponse()
    response.ret = 0
    return ProtobufResponse(response)


def read(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    id = request._proto.id

    m = MailManager(server_id, char_id)
    m.read(id)

    response = MailOpenResponse()
    response.ret = 0
    return ProtobufResponse(response)


def delete(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    id = request._proto.id

    m = MailManager(server_id, char_id)
    m.delete(id)

    response = MailDeleteResponse()
    response.ret = 0
    return ProtobufResponse(response)


def get_attachment(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    id = request._proto.id

    m = MailManager(server_id, char_id)
    package = m.get_attachment(id)

    response = MailGetAttachmentResponse()
    response.ret = 0
    response.attachment.MergeFrom(package.make_protomsg())
    return ProtobufResponse(response)

