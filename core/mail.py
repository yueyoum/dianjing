# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mail
Date Created:   2015-07-30 16:06
Description:

"""

import arrow

from dianjing.exception import GameException

from core.mongo import MongoMail, MongoCharacter
from core.character import Character
from core.package import Drop
from core.resource import Resource

from config import ConfigErrorMessage
from config.settings import MAIL_KEEP_DAYS, MAIL_CLEAN_AT

from utils.functional import make_string_id
from utils.message import MessagePipe

from protomsg.mail_pb2 import (
    MailNotify,
    MailRemoveNotify,
    MAIL_FROM_SYSTEM,
    MAIL_FROM_USER,
)

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT


def get_mail_clean_time():
    now = arrow.utcnow().replace(days=-MAIL_KEEP_DAYS)
    date_string = "{0} {1}".format(now.format("YYYY-MM-DD"), MAIL_CLEAN_AT)
    date = arrow.get(date_string, "YYYY-MM-DD HH:mm:ssZ").to('UTC')

    if date < now:
        date = date.replace(days=1)

    return date


class MailManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoMail.db(server_id).find_one({'_id': char_id}, {'_id': 1})
        if not doc:
            doc = MongoMail.document()
            doc['_id'] = char_id
            MongoMail.db(server_id).insert_one(doc)

    def get_mail(self, mail_id):
        doc = MongoMail.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'mails.{0}'.format(mail_id): 1}
        )

        return doc['mails'].get(mail_id, None)

    def send(self, to_id, content):
        # 聊天
        to_id = int(to_id)
        target_doc = MongoCharacter.db(self.server_id).find_one({'_id': to_id}, {'_id': 1})
        if not target_doc:
            raise GameException(ConfigErrorMessage.get_error_id("CHAR_NOT_EXIST"))

        self_doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'name': 1})

        title = u"来自 {0} 的邮件".format(self_doc['name'])
        MailManager(self.server_id, to_id).add(title, content, from_id=self.char_id)

    def add(self, title, content, attachment="", from_id=0, function=0):
        doc = MongoMail.document_mail()
        doc['from_id'] = from_id
        doc['title'] = title
        doc['content'] = content
        doc['attachment'] = attachment
        doc['create_at'] = arrow.utcnow().timestamp
        doc['function'] = function

        mail_id = make_string_id()

        MongoMail.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'mails.{0}'.format(mail_id): doc}}
        )

        self.send_notify(ids=[mail_id])

    def delete(self, mail_id):
        key = "mails.{0}".format(mail_id)
        MongoMail.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {key: 1}}
        )

        self.send_remove_notify([mail_id])

    def open(self, mail_id):
        if not self.get_mail(mail_id):
            raise GameException(ConfigErrorMessage.get_error_id("MAIL_NOT_EXISTS"))

        MongoMail.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'mails.{0}.has_read'.format(mail_id): True}}
        )

        self.send_notify(ids=[mail_id])

    def get_attachment(self, mail_id):
        this_mail = self.get_mail(mail_id)
        if not this_mail:
            raise GameException(ConfigErrorMessage.get_error_id("MAIL_NOT_EXISTS"))

        attachment = this_mail['attachment']
        if not attachment:
            raise GameException(ConfigErrorMessage.get_error_id("MAIL_HAS_NO_ATTACHMENT"))

        drop = Drop.loads_from_json(attachment)
        message = u"Attachment from mail: {0}".format(this_mail['title'])
        Resource(self.server_id, self.char_id).save_drop(drop, message=message)

        MongoMail.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'mails.{0}.attachment'.format(mail_id): ""}}
        )

        self.send_notify(ids=[mail_id])
        return drop

    def clean_expired(self):
        limit_timestamp = get_mail_clean_time().timestamp

        doc = MongoMail.db(self.server_id).find_one({'_id': self.char_id}, {'mails': 1})
        expired = []

        for k, v in doc['mails'].iteritems():
            remained_seconds = v['create_at'] - limit_timestamp
            if remained_seconds < 0:
                expired.append(k)

        if expired:
            updater = {"mails.{0}".format(i): 1 for i in expired}

            MongoMail.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$unset': updater}
            )

            self.send_remove_notify(expired)
        return len(expired)

    def send_remove_notify(self, ids):
        notify = MailRemoveNotify()
        notify.ids.extend(ids)
        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self, ids=None):
        if ids:
            projection = {"mails.{0}".format(i): 1 for i in ids}
            act = ACT_UPDATE
        else:
            projection = {"mails": 1}
            act = ACT_INIT

        doc = MongoMail.db(self.server_id).find_one({'_id': self.char_id}, projection)
        notify = MailNotify()
        notify.act = act

        limit_timestamp = get_mail_clean_time().timestamp

        for k, v in doc['mails'].iteritems():
            notify_mail = notify.mails.add()
            notify_mail.id = k

            if v['from_id']:
                # char
                notify_mail.mail_from.from_type = MAIL_FROM_USER
                notify_mail.mail_from.char.MergeFrom(Character(self.server_id, v['from_id']).make_protomsg())
            else:
                notify_mail.mail_from.from_type = MAIL_FROM_SYSTEM

            notify_mail.title = v['title']
            notify_mail.content = v['content']
            notify_mail.has_read = v['has_read']
            notify_mail.create_at = v['create_at']

            remained_seconds = v['create_at'] - limit_timestamp
            if remained_seconds < 0:
                remained_seconds = 0

            notify_mail.remained_seconds = remained_seconds

            if v['attachment']:
                notify_mail.attachment.MergeFrom(Drop.loads_from_json(v['attachment']).make_protomsg())

            function = v.get('function', 0)
            if function:
                notify_mail.function = function

        MessagePipe(self.char_id).put(msg=notify)
