# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-03 15:09
Description:

"""

from core.abstract import AbstractClub
from core.db import get_mongo_db
from core.staff import Staff
from core.signals import match_staffs_set_done_signal

from utils.message import MessagePipe
from config import ConfigClubLevel

from protomsg.club_pb2 import ClubNotify

class Club(AbstractClub):
    def __init__(self, server_id, char_id):
        super(Club, self).__init__()

        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)

        self.load_data()


    def load_data(self):
        char = self.mongo.character.find_one({'_id': self.char_id}, {'club': 1, 'name': 1, 'staffs': 1})
        club = char['club']
        staffs = char.get('staffs', {})

        self.id = self.char_id
        self.name = club['name']
        self.manager_name = char['name']
        self.flag = club['flag']
        self.level = club['level']
        self.renown = club['renown']
        self.vip = club['vip']
        self.exp = club['exp']
        self.gold = club['gold']
        # FIXME
        self.diamond = int(club['diamond'])
        self.policy = club.get('policy', 1)

        self.match_staffs = club.get('match_staffs', [])
        self.tibu_staffs = club.get('tibu_staffs', [])

        for k, v in staffs.iteritems():
            self.staffs[int(k)] = Staff(int(k), v)


    def set_policy(self, policy):
        # TODO check
        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {'club.policy': policy}}
        )

        self.policy = policy
        self.send_notify()


    def set_match_staffs(self, staff_ids):
        # TODO check
        if len(staff_ids) != 10:
            raise RuntimeError("staff_ids is not 10 elements")

        match_staffs = staff_ids[:5]
        tibu_staffs = staff_ids[5:]

        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {
                'club.match_staffs': match_staffs,
                'club.tibu_staffs': tibu_staffs
            }}
        )

        if all([i != 0 for i in match_staffs]):
            # set done
            match_staffs_set_done_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                match_staffs=match_staffs
            )

        self.load_data()
        self.send_notify()


    def update(self, **kwargs):
        renown = kwargs.get('renown', 0)
        gold = kwargs.get('gold', 0)
        diamond = kwargs.get('diamond', 0)

        self.gold += gold
        self.diamond += diamond

        next_level_id = ConfigClubLevel.get(self.level).next_level_id
        if next_level_id:
            self.renown += renown

            need_renown = ConfigClubLevel.get(self.level).renown
            if self.renown >= need_renown:
                self.renown -= need_renown
                self.level = next_level_id


        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {
                'club.level': self.level,
                'club.renown': self.renown,
                'club.gold': self.gold,
                'club.diamond': self.diamond,
            }}
        )

        self.send_notify()


    def send_notify(self):
        msg = self.make_protomsg()
        notify = ClubNotify()
        notify.club.MergeFrom(msg)
        MessagePipe(self.char_id).put(notify)
