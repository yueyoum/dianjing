# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       sponsor
Date Created:   2015-09-17 14:04
Description:

"""
from dianjing.exception import GameException

from core.mongo import MongoSponsor, MongoCharacter
from core.friend import FriendManager
from core.building import BuildingSponsorCenter

from utils.message import MessagePipe
from config import ConfigErrorMessage, ConfigBuilding

from protomsg.spread_pb2 import SponsorNotify


class SponsorManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoSponsor.exist(server_id, char_id):
            doc = MongoSponsor.document()
            doc['_id'] = char_id
            MongoSponsor.db(server_id).insert_one(doc)

    def get_sponsor_to_id(self):
        doc = MongoSponsor.db(self.server_id).find_one({'_id': self.char_id}, {'sponsor_to_id': 1})
        return doc['sponsor_to_id']

    def sponsor(self, target_id):
        # 添加赞助
        target_id = int(target_id)
        doc = MongoSponsor.db(self.server_id).find_one({'_id': self.char_id}, {'sponsor_to_id': 1})

        if doc['sponsor_to_id']:
            raise GameException(ConfigErrorMessage.get_error_id("SPONSOR_ALREADY_SPONSOR"))

        if not FriendManager(self.server_id, self.char_id).check_friend_exist(target_id):
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_NOT_OK"))

        MongoSponsor.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'sponsor_to_id': target_id}}
        )

        self.send_notify()
        SponsorManager(self.server_id, target_id).someone_sponsor_me(self.char_id)

    def someone_sponsor_me(self, sponsor_id):
        MongoSponsor.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'sponsors.{0}'.format(sponsor_id): 0}}
        )

        self.send_notify()

        # 设置上级log
        sponsor_to_id = self.get_sponsor_to_id()
        if sponsor_to_id:
            SponsorManager(self.server_id, sponsor_to_id).add_sponsor_log(self.char_id)

    def get_income(self):
        doc = MongoSponsor.db(self.server_id).find_one({'_id': self.char_id}, {'income': 1})
        if not doc['income']:
            return

        # drop = Drop()
        # drop.diamond = doc['income']
        # message = u"Sponsor income"
        # Resource(self.server_id, self.char_id).save_drop(drop, message)

        MongoSponsor.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'income': 0}}
        )

        self.send_notify()

    def add_purchase_income(self, from_id, real_from_id, purchase_got, step):
        if step > 2:
            return

        level = BuildingSponsorCenter(self.server_id, self.char_id).current_level()
        config = ConfigBuilding.get(BuildingSponsorCenter.BUILDING_ID).get_level(level)

        value = config.effect.get('2', 1) if step == 1 else config.effect.get('2', 1)

        got = int(purchase_got * value / 100.0)
        if not got:
            got = 1

        MongoSponsor.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'income': got,
                'sponsors.{0}'.format(from_id): got
            }}
        )

        self.add_income_log(from_id, got)

        sponsor_to_id = self.get_sponsor_to_id()
        if sponsor_to_id:
            SponsorManager(self.server_id, sponsor_to_id).add_purchase_income(self.char_id, real_from_id, purchase_got,
                                                                              step + 1)

    def add_sponsor_log(self, from_id):
        from_doc = MongoCharacter.db(self.server_id).find_one(
            {'_id': from_id},
            {'club.name': 1}
        )

        data = [1, [from_doc['club']['name']]]
        MongoSponsor.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {'logs': {
                '$each': [data],
                '$slice': -50
            }}},
        )

        self.send_notify()

    def add_income_log(self, from_id, income):
        from_doc = MongoCharacter.db(self.server_id).find_one(
            {'_id': from_id},
            {'club.name': 1}
        )

        data = [2, [from_doc['club']['name'], str(income)]]
        MongoSponsor.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {'logs': {
                '$each': [data],
                '$slice': -50
            }}},
        )

        self.send_notify()

    def purchase(self, purchase_got):
        sponsor_to_id = self.get_sponsor_to_id()
        if not sponsor_to_id:
            return

        SponsorManager(self.server_id, sponsor_to_id).add_purchase_income(self.char_id, self.char_id, purchase_got, 1)

    def send_notify(self):
        doc = MongoSponsor.db(self.server_id).find_one({'_id': self.char_id})

        notify = SponsorNotify()
        if not doc['sponsor_to_id']:
            notify.sponsor_to = ""
        else:
            sponsor_to_doc = MongoCharacter.db(self.server_id).find_one({'_id': doc['sponsor_to_id']}, {'club.name': 1})
            notify.sponsor_to = sponsor_to_doc['club']['name']

        notify.total_income = doc['income']
        for template_id, args in doc['logs']:
            notify_log = notify.logs.add()
            notify_log.template_id = template_id
            notify_log.args.extend(args)

        sponsor_ids = [int(k) for k in doc['sponsors'].keys()]
        sponsors_doc = MongoCharacter.db(self.server_id).find({'_id': {'$in': sponsor_ids}},
                                                              {'club.name': 1, 'club.flag': 1})
        sponsors = {d['_id']: d for d in sponsors_doc}

        for sid in sponsor_ids:
            notify_sponsor = notify.sponsors.add()
            notify_sponsor.club_flag = sponsors[sid]['club']['flag']
            notify_sponsor.club_name = sponsors[sid]['club']['name']
            notify_sponsor.income = doc['sponsors'][str(sid)]

            this_sponsor_doc = MongoSponsor.db(self.server_id).find_one({'_id': sid}, {'sponsors': 1})
            notify_sponsor.sponsor_amount = len(this_sponsor_doc['sponsors'])

        MessagePipe(self.char_id).put(msg=notify)
