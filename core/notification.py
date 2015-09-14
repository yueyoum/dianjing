# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       notification
Date Created:   2015-08-04 18:21
Description:

"""

import arrow

from dianjing.exception import GameException
from core.mongo import MongoNotification

from utils.functional import make_string_id
from utils.message import MessagePipe

from config.settings import NOTIFICATION_MAX_AMOUNT
from config import ConfigErrorMessage

from protomsg.notification_pb2 import NotificationNotify, NotificationRemoveNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT


# 各种通知
class Notification(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoNotification.exist(server_id, self.char_id):
            doc = MongoNotification.document()
            doc['_id'] = self.char_id
            MongoNotification.db(server_id).insert_one(doc)

    def has_notification(self, noti_id):
        doc = MongoNotification.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'notis.{0}'.format(noti_id): 1}
        )

        return noti_id in doc['notis']

    def add_league_notification(self, win, target, score_got, gold_got, score_rank):
        tp = 1 if win else 2
        args = (target, str(score_got), str(gold_got), str(score_rank))
        return self._add(tp, args)

    def add_ladder_notification(self, win, from_name, current_order, ladder_score):
        tp = 3 if win else 4
        args = (from_name, str(current_order), str(ladder_score))
        return self._add(tp, args)

    def _add(self, tp, args):
        doc = MongoNotification.db(self.server_id).find_one({'_id': self.char_id}, {'notis': 1})
        notis = [(k, v['tp'], v['args'], v['timestamp']) for k, v in doc['notis'].iteritems()]
        notis.sort(key=lambda item: item[3])

        remove_ids = []
        while len(notis) > NOTIFICATION_MAX_AMOUNT - 1:
            x = notis.pop(0)
            remove_ids.append(x[0])

        noti_id = make_string_id()
        data = MongoNotification.document_notification()
        data['tp'] = tp
        data['args'] = args
        data['timestamp'] = arrow.utcnow().timestamp
        data['opened'] = False

        updater = {'$set': {
            'notis.{0}'.format(noti_id): data
        }}

        if remove_ids:
            updater['$unset'] = {'notis.{0}'.format(i): 1 for i in remove_ids}

            notify = NotificationRemoveNotify()
            notify.ids.extend(remove_ids)
            MessagePipe(self.char_id).put(msg=notify)

        MongoNotification.db(self.server_id).update_one(
            {'_id': self.char_id},
            updater
        )

        self.send_notify([noti_id])
        return noti_id

    def open(self, noti_id):
        if not self.has_notification(noti_id):
            raise GameException(ConfigErrorMessage.get_error_id("NOTIFICATION_NOT_EXIST"))

        MongoNotification.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'notis.{0}.opened'.format(noti_id): True
            }}
        )

        self.send_notify(ids=[noti_id])

    def delete(self, noti_id):
        if not self.has_notification(noti_id):
            raise GameException(ConfigErrorMessage.get_error_id("NOTIFICATION_NOT_EXIST"))

        MongoNotification.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {
                'notis.{0}'.format(noti_id): 1
            }}
        )

        notify = NotificationRemoveNotify()
        notify.ids.append(noti_id)
        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self, ids=None):
        if ids:
            projection = {'notis.{0}'.format(i): 1 for i in ids}
            act = ACT_UPDATE
        else:
            projection = {'notis': 1}
            act = ACT_INIT

        doc = MongoNotification.db(self.server_id).find_one({'_id': self.char_id}, projection)

        notify = NotificationNotify()
        notify.act = act

        for k, v in doc['notis'].iteritems():
            notify_noti = notify.notifications.add()
            notify_noti.id = k
            notify_noti.timestamp = v['timestamp']
            notify_noti.tp = v['tp']
            notify_noti.args.extend(v['args'])
            notify_noti.opened = v['opened']

        MessagePipe(self.char_id).put(msg=notify)
