# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-03 15:09
Description:

"""
from core.db import get_mongo_db

from utils.message import MessagePipe

from protomsg.club_pb2 import ClubNotify

class ClubManager(object):
    def __init__(self, server_id, char_id):
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)

    def add(self, **kwargs):
        gold = kwargs.get('gold', 0)
        self.club.gold += gold
        self.club.save()
        self.send_notify()

    def send_notify(self):
        char = self.mongo.character.find_one({'_id': self.char_id})
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

        MessagePipe(self.char_id).put(msg)
