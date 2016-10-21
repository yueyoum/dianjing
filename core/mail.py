# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mail
Date Created:   2015-07-30 16:06
Description:

"""

import arrow
import base64
import contextlib

from django.conf import settings
from django.db.models import Q
from django.db import connection

from apps.server.models import Server as ModelServer
from apps.character.models import Character as ModelCharacter
from apps.config.models import Mail as GMMail
from apps.history_record.models import MailHistoryRecord

from dianjing.exception import GameException

from core.mongo import MongoMail, MongoSharedMail, MongoCharacter
from core.resource import ResourceClassification
from core.club import Club
from core.vip import VIP

from config import ConfigErrorMessage
from config.settings import MAIL_KEEP_DAYS, MAIL_CLEAN_AT

from utils.functional import make_string_id
from utils.message import MessagePipe
from utils.operation_log import OperationLog

from protomsg.mail_pb2 import (
    MailNotify,
    MailRemoveNotify,
    MAIL_FROM_SYSTEM,
    MAIL_FROM_USER,
)

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT


class AdminMailManager(object):
    __slots__ = ['send_ids', 'done_ids', 'mails']

    def __init__(self):
        self.send_ids = []
        self.done_ids = []
        self.mails = []

    def fetch(self, mail_id=None):
        connection.close()

        if mail_id:
            condition = Q(id=mail_id)
        else:
            now = arrow.utcnow().format("YYYY-MM-DD HH:mm:ssZ")
            condition = Q(send_at__lte=now) & Q(status=0)

        self.mails = GMMail.objects.filter(condition)
        self.mails = list(self.mails)
        self.send_ids = [m.id for m in self.mails]

    def start_send(self):
        for m in self.mails:
            # lock
            m.status = 1
            m.save()

            try:
                self._send_one_mail(m)
            except:
                m.status = 3
                m.save()
                raise
            else:
                m.status = 2
                m.save()
                self.done_ids.append(m.id)

    def _send_one_mail(self, m):
        # lock
        m.status = 1
        m.save()

        if m.items:
            rc = ResourceClassification.classify(m.get_parsed_items())
            attachment = rc.to_json()
        else:
            attachment = ""

        if m.condition_type == 1:
            # 全部服务器
            for s in ModelServer.objects.all():
                self._send_to_one_server(s.id, m, attachment)
        elif m.condition_type == 2:
            # 指定服务器
            for sid in m.get_parsed_condition_value():
                self._send_to_one_server(sid, m, attachment)
        elif m.condition_type == 3:
            # 指定排除服务器
            values = m.get_parsed_condition_value()
            for s in ModelServer.objects.exclude(id__in=values):
                self._send_to_one_server(s.id, m, attachment)
        elif m.condition_type == 11:
            # 指定角色ID
            values = m.get_parsed_condition_value()
            chars = ModelCharacter.objects.filter(id__in=values)
            for c in chars:
                self._send_to_one_char(c.server_id, c.id, m, attachment)

    @staticmethod
    def _send_to_one_server(sid, m, attachment):
        if m.has_condition():
            club_level = m.condition_club_level
            vip_level = m.condition_vip_level

            if m.condition_login_at_1:
                login_range = [arrow.get(m.condition_login_at_1), arrow.get(m.condition_login_at_2)]
            else:
                login_range = None

            exclude_char_ids = m.get_parsed_condition_exclude_chars()

            result_list = []
            if club_level or login_range:
                result_list.append(Club.query_char_ids(sid, min_level=club_level, login_range=login_range))

            if vip_level:
                result_list.append(VIP.query_char_ids(sid, vip_level))

            if not result_list:
                return

            result = set(result_list[0])
            for i in range(1, len(result_list)):
                result &= set(result_list[i])

            result -= set(exclude_char_ids)

            to_char_ids = list(result)
            if not to_char_ids:
                return
        else:
            to_char_ids = ModelCharacter.objects.filter(server_id=sid).values_list('id', flat=True)
            to_char_ids = list(to_char_ids)

        SharedMail(sid).add(to_char_ids, m.title, m.content, attachment=attachment)

    @staticmethod
    def _send_to_one_char(sid, cid, m, attachment):
        mail = MailManager(sid, cid)
        mail.add(m.title, m.content, attachment=attachment)


class SharedMail(object):
    __slots__ = ['server_id']

    def __init__(self, server_id):
        self.server_id = server_id

    def add(self, for_char_ids, title, content, attachment="", from_id=0, function=0):
        doc = MongoMail.document_mail()

        doc['id'] = make_string_id()
        doc['for_char_ids'] = for_char_ids

        doc['from_id'] = from_id
        doc['title'] = title
        doc['content'] = content
        doc['attachment'] = attachment
        doc['create_at'] = arrow.utcnow().timestamp
        doc['function'] = function

        MongoSharedMail.db(self.server_id).insert_one(doc)

        # 立即给最近登陆操作的人发送通知
        recent_char_ids = OperationLog.get_recent_action_char_ids(self.server_id)
        for cid in recent_char_ids:
            MailManager(self.server_id, cid).send_notify()

    def fetch(self, char_id):
        return MongoSharedMail.db(self.server_id).find({'for_char_ids': {'$in': [char_id]}})

    @contextlib.contextmanager
    def fetch_and_clean(self, char_id):
        docs = self.fetch(char_id)

        ids = []
        mails = []
        for doc in docs:
            ids.append(doc['_id'])
            mails.append(doc)

        yield mails

        if ids:
            MongoSharedMail.db(self.server_id).update_many(
                {'_id': {'$in': ids}},
                {'for_char_ids': {'$pull': char_id}}
            )


def get_mail_clean_time():
    limit = arrow.utcnow().to(settings.TIME_ZONE).replace(days=-MAIL_KEEP_DAYS)
    date_string = "{0} {1}".format(limit.format("YYYY-MM-DD"), MAIL_CLEAN_AT)
    date = arrow.get(date_string, "YYYY-MM-DD HH:mm:ssZ").to('UTC')

    if date < limit:
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

        # try get shared mail
        with SharedMail(server_id).fetch_and_clean(char_id) as shared_mails:
            for sm in shared_mails:
                if sm['_id'] in doc['mails']:
                    # 防止因为不确定原因导致的 重复添加邮件问题
                    continue

                self.add(
                    title=sm['title'],
                    content=sm['content'],
                    mail_id=sm['_id'],
                    attachment=sm['attachment'],
                    create_at=sm['create_at'],
                    from_id=sm['from_id'],
                    function=sm['function'],
                    send_notify=False
                )

    @staticmethod
    def cronjob(server_id):
        # 删除过期邮件
        cleaned_amount = 0
        doc = MongoMail.db(server_id).find({}, {'_id': 1})
        for d in doc:
            mm = MailManager(server_id, d['_id'])
            cleaned_amount += mm.clean_expired()

        return cleaned_amount

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

    def add(self, title, content, mail_id=None, attachment="", create_at=None, from_id=0, function=0, send_notify=True):
        if create_at:
            now = arrow.get(create_at)
        else:
            now = arrow.utcnow()

        doc = MongoMail.document_mail()
        doc['from_id'] = from_id
        doc['title'] = title
        doc['content'] = content
        doc['attachment'] = attachment
        doc['create_at'] = now.timestamp
        doc['function'] = function

        # doc['data'] = base64.b64encode(data)

        if not mail_id:
            mail_id = make_string_id()

        MongoMail.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'mails.{0}'.format(mail_id): doc}}
        )

        MailHistoryRecord.create(
            _id=mail_id,
            from_id=from_id,
            to_id=self.char_id,
            title=title,
            content=content,
            attachment=attachment,
            function=function,
            create_at=now.format("YYYY-MM-DD HH:mm:ssZ")
        )

        if send_notify:
            self.send_notify(ids=[mail_id])

    def delete(self, mail_id):
        key = "mails.{0}".format(mail_id)
        MongoMail.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {key: 1}}
        )

        self.send_remove_notify([mail_id])

    def open(self, mail_id):
        from apps.history_record.models import MailHistoryRecord

        if not self.get_mail(mail_id):
            raise GameException(ConfigErrorMessage.get_error_id("MAIL_NOT_EXISTS"))

        MongoMail.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'mails.{0}.has_read'.format(mail_id): True}}
        )

        MailHistoryRecord.set_read(mail_id)
        self.send_notify(ids=[mail_id])

    def get_attachment(self, mail_id):
        this_mail = self.get_mail(mail_id)
        if not this_mail:
            raise GameException(ConfigErrorMessage.get_error_id("MAIL_NOT_EXISTS"))

        attachment = this_mail['attachment']
        if not attachment:
            raise GameException(ConfigErrorMessage.get_error_id("MAIL_HAS_NO_ATTACHMENT"))

        rc = ResourceClassification.load_from_json(attachment)
        rc.add(self.server_id, self.char_id)

        MongoMail.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'mails.{0}.attachment'.format(mail_id): ""}}
        )

        self.send_notify(ids=[mail_id])
        return rc

    def clean_expired(self):
        limit_timestamp = get_mail_clean_time().timestamp

        doc = MongoMail.db(self.server_id).find_one({'_id': self.char_id}, {'mails': 1})
        expired = []

        total_amount = len(doc['mails'])

        for k, v in doc['mails'].iteritems():
            if v['create_at'] <= limit_timestamp:
                expired.append(k)

        if expired:
            if len(expired) == total_amount:
                MongoMail.db(self.server_id).delete_one({'_id': self.char_id})
            else:
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
                # XXX
                notify_mail.mail_from.club.MergeFrom(Club(self.server_id, v['from_id']).make_protomsg())
            else:
                notify_mail.mail_from.from_type = MAIL_FROM_SYSTEM

            notify_mail.title = v['title']
            notify_mail.content = v['content']
            notify_mail.has_read = v['has_read']
            notify_mail.create_at = v['create_at']
            notify_mail.function = v['function']
            if v.get('data', None):
                notify_mail.data = base64.b64decode(v['data'])

            remained_seconds = v['create_at'] - limit_timestamp
            if remained_seconds < 0:
                remained_seconds = 0

            notify_mail.remained_seconds = remained_seconds

            if v['attachment']:
                notify_mail.attachment.MergeFrom(ResourceClassification.load_from_json(v['attachment']).make_protomsg())

            function = v.get('function', 0)
            if function:
                notify_mail.function = function

        MessagePipe(self.char_id).put(msg=notify)
