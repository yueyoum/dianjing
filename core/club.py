# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-03 15:09
Description:

"""
from itertools import chain
from core.db import get_mongo_db
from utils.message import MessagePipe

from protomsg.club_pb2 import ClubNotify


class ClubManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)

    def set_policy(self, policy):
        # TODO check
        self.mongo.character.update(
            {'_id': self.char_id},
            {'$set': {'club.policy': policy}}
        )

        self.send_notify()

    def set_match_staffs(self, staff_ids):
        # TODO check
        if len(staff_ids) != 10:
            raise RuntimeError("staff_ids is not 10 elements")

        match_staffs = staff_ids[:5]
        tibu_staffs = staff_ids[5:]

        self.mongo.character.update(
            {'_id': self.char_id},
            {'$set': {
                'club.match_staffs': match_staffs,
                'club.tibu_staffs': tibu_staffs
            }}
        )

        self.send_notify()


    def send_notify(self):
        char = self.mongo.character.find_one({'_id': self.char_id}, {'club': 1, 'name': 1})
        club = char['club']

        msg = ClubNotify()
        msg.club.id = self.char_id
        msg.club.name = club['name']
        msg.club.manager = char['name']
        msg.club.flag = club['flag']
        msg.club.level = club['level']
        msg.club.renown = club['renown']
        msg.club.vip = club['vip']
        msg.club.exp = club['exp']
        msg.club.gold = club['gold']
        msg.club.diamond = int(club['diamond'])

        # TODO
        msg.club.max_renown = 1000

        match_staffs = club.get('match_staffs', [])
        while len(match_staffs) < 5:
            match_staffs.append(0)

        tibu_staffs = club.get('tibu_staffs', [])
        while len(tibu_staffs) < 5:
            tibu_staffs.append(0)

        for i in chain(match_staffs, tibu_staffs):
            msg_match_staff = msg.club.match_staffs.add()
            if i == 0:
                msg_match_staff.id = 0
                msg_match_staff.level = 0
            else:
                msg_match_staff.id = i
                msg_match_staff.level = 0

        policy = club.get('policy', 0)
        if policy:
            msg.club.policy = policy

        MessagePipe(self.char_id).put(msg)
