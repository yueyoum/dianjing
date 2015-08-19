# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mail
Date Created:   2015-07-30 16:06
Description:

"""

import uuid
import arrow

from dianjing.exception import GameException

from core.db import MongoDB
from core.mongo import Document
from core.character import Character
from core.package import Package
from core.resource import Resource

from config import ConfigErrorMessage

from utils.message import MessagePipe

from protomsg.mail_pb2 import MailNotify, MailRemoveNotify, MAIL_FROM_SYSTEM, MAIL_FROM_USER
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT



class MailManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = MongoDB.get(server_id)

        doc = self.mongo.mail.find_one({'_id': char_id}, {'_id': 1})
        if not doc:
            doc = Document.get("mail")
            doc['_id'] = char_id
            self.mongo.mail.insert_one(doc)


    def send(self, to_id, content):
        to_id = int(to_id)
        char = self.mongo.character.find_one({'_id': to_id}, {'name': 1})
        if not char:
            raise GameException( ConfigErrorMessage.get_error_id("CHAR_NOT_EXIST") )

        title = u"来自 {0} 的邮件".format(char['name'])
        MailManager(self.server_id, to_id).add(title, content, from_id=self.char_id)


    def add(self, title, content, attachment="", from_id=0):
        doc = Document.get("mail.embedded")
        doc['from_id'] = from_id
        doc['title'] = title
        doc['content'] = content
        doc['attachment'] = attachment
        doc['create_at'] = arrow.utcnow().timestamp

        mid = uuid.uuid4()

        self.mongo.mail.update_one(
            {'_id': self.char_id},
            {'$set': {'mails.{0}'.format(mid): doc}}
        )

        self.send_notify(act=ACT_UPDATE, ids=[mid])

    def delete(self, mid):
        key = "mails.{0}".format(mid)
        self.mongo.mail.update_one(
            {'_id': self.char_id},
            {'$unset': {key: 1}}
        )

        notify = MailRemoveNotify()
        notify.ids.append(mid)

        MessagePipe(self.char_id).put(msg=notify)


    def read(self, mid):
        key = "mails.{0}".format(mid)
        doc = self.mongo.mail.find_one(
            {'_id': self.char_id},
            {key: 1}
        )

        if mid not in doc['mails']:
            raise GameException( ConfigErrorMessage.get_error_id("MAIL_NOT_EXISTS") )

        self.mongo.mail.update_one(
            {'_id': self.char_id},
            {'$set': {'mails.{0}.has_read'.format(mid): True}}
        )

        self.send_notify(act=ACT_UPDATE, ids=[mid])


    def get_attachment(self, mid):
        key = "mails.{0}".format(mid)
        doc = self.mongo.mail.find_one(
            {'_id': self.char_id},
            {key: 1}
        )

        this_mail = doc['mails'].get(mid, None)
        if not this_mail:
            raise GameException( ConfigErrorMessage.get_error_id("MAIL_NOT_EXISTS") )

        attachment = this_mail['attachment']
        if not attachment:
            raise GameException( ConfigErrorMessage.get_error_id("MAIL_HAS_NO_ATTACHMENT") )

        package = Package.loads(attachment)
        Resource(self.server_id, self.char_id).add_package(package)

        self.mongo.mail.update_one(
            {'_id': self.char_id},
            {'$set': {'mails.{0}.attachment'.format(mid): ""}}
        )

        self.send_notify(act=ACT_UPDATE, ids=[mid])

        return package


    def send_notify(self, act=ACT_INIT, ids=None):
        if ids:
            projection = {"mails.{0}".format(i): 1 for i in ids}
        else:
            projection = {"mails": 1}

        doc = self.mongo.mail.find_one({'_id': self.char_id}, projection)
        notify = MailNotify()
        notify.act = act

        for k, v in doc['mails'].iteritems():
            notify_mail = notify.mails.add()
            notify_mail.id = k

            if v['from_id'] > 0:
                # char
                notify_mail.mail_from.from_type = MAIL_FROM_USER
                notify_mail.mail_from.char.MergeFrom(Character(self.server_id, self.char_id).make_protomsg())
            else:
                notify_mail.mail_from.from_type = MAIL_FROM_SYSTEM

            notify_mail.title = v['title']
            notify_mail.content = v['content']
            notify_mail.has_read = v['has_read']
            notify_mail.create_at = v['create_at']
            # TODO
            notify_mail.remained_seconds = 1000

            if v['attachment']:
                notify_mail.attachment.MergeFrom(Package.loads(v['attachment']).make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
