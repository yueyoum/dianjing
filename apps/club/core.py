# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       core
Date Created:   2015-04-30 15:55
Description:

"""

from apps.club.models import Club as ModelClub

from utils.message import MessagePipe

from protomsg.club_pb2 import ClubNotify

class ClubManager(object):
    def __init__(self, char_id):
        self.char_id = char_id
        self.club = ModelClub.objects.get(char_id=char_id)

    def add(self, **kwargs):
        gold = kwargs.get('gold', 0)
        self.club.gold += gold
        self.club.save()
        self.send_notify()

    def send_notify(self):
        msg = ClubNotify()
        msg.club.id = self.club.id
        msg.club.name = self.club.name
        msg.club.manager = self.club.char_name
        msg.club.flag = self.club.flag
        msg.club.level = self.club.level
        msg.club.renown = self.club.renown
        msg.club.vip = self.club.vip
        msg.club.exp = self.club.exp
        msg.club.gold = self.club.gold
        msg.club.sycee = self.club.sycee

        MessagePipe(self.char_id).put(msg)
