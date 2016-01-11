# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-11-12 16:01
Description:

"""

from core.mongo import MongoLadder
from core.abstract import AbstractStaff, AbstractClub
from core.club import Club
from core.match import ClubMatch
from core.package import Drop
from core.notification import Notification
from core.signals import ladder_match_signal

from config import (
    ConfigLadderRankReward,
    ConfigStaff,
)


class LadderNPCStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, data):
        super(LadderNPCStaff, self).__init__()

        self.id = data['id']
        config = ConfigStaff.get(self.id)

        # TODO
        self.level = 1
        self.race = config.race
        skill_level = data.get('skill_level', 1)
        self.skills = {i: skill_level for i in config.skill_ids}

        self.caozuo = data['caozuo']
        self.baobing = data['baobing']
        self.jingying = data['jingying']
        self.zhanshu = data['zhanshu']


class LadderNPCClub(AbstractClub):
    __slots__ = ['order', 'score']

    def __init__(self, ladder_id, club_name, manager_name, club_flag, staffs, order, score):
        super(LadderNPCClub, self).__init__()
        self.id = ladder_id
        self.name = club_name
        self.manager_name = manager_name
        self.flag = club_flag
        # TODO
        self.policy = 1

        for s in staffs:
            self.match_staffs.append(s['id'])
            self.staffs[s['id']] = LadderNPCStaff(s)

        self.qianban_affect()

        self.order = order
        self.score = score


class LadderRealClub(Club):
    def __init__(self, server_id, club_id, order, score):
        super(LadderRealClub, self).__init__(server_id, club_id)
        self.order = order
        self.score = score


class LadderClub(object):
    def __new__(cls, server_id, club):
        # club 是 Ladder 数据
        if club['club_name']:
            # NPC
            return LadderNPCClub(club['_id'], club['club_name'], club['manager_name'], club['club_flag'],
                                 club['staffs'], club['order'], club['score'])

        return LadderRealClub(server_id, int(club['_id']), club['order'], club['score'])


class LadderMatch(object):
    def __init__(self, server_id, club_one, club_two):
        self.server_id = server_id
        self.club_one = club_one
        self.club_two = club_two

        self.club_one_object = LadderClub(self.server_id, self.club_one)
        self.club_two_object = LadderClub(self.server_id, self.club_two)

        self.club_one_win = False
        self.club_one_add_score = 0

    def start(self):
        return ClubMatch(self.club_one_object, self.club_two_object).start()

    def end_match(self, club_one_win):
        if club_one_win == self.club_one_object.id:
            self.club_one_win = True
        else:
            self.club_one_win = False

        self.after_match()
        return self.club_one_add_score

    def after_match(self):
        # 记录天梯战报
        from core.ladder import Ladder
        order_changed = self.club_one['order'] - self.club_two['order']

        # final_club_one_order = self.club_one['order']
        final_club_two_order = self.club_two['order']

        if self.club_one_win:
            self.club_one_add_score = 10
            if order_changed > 0:
                # exchange the order
                MongoLadder.db(self.server_id).update_one(
                    {'_id': self.club_one['_id']},
                    {'$set': {'order': self.club_two['order']}}
                )

                MongoLadder.db(self.server_id).update_one(
                    {'_id': self.club_two['_id']},
                    {'$set': {'order': self.club_one['order']}}
                )

                # final_club_one_order = self.club_two['order']
                final_club_two_order = self.club_one['order']

                self_log = (1, (self.club_two_object.name, str(order_changed)))
                target_log = (4, (self.club_one_object.name, str(order_changed)))
            else:
                self_log = (5, (self.club_two_object.name,))
                target_log = (6, (self.club_one_object.name,))
        else:
            self.club_one_add_score = 5
            self_log = (2, (self.club_two_object.name,))
            target_log = (3, (self.club_one_object.name,))

        ladder_one = Ladder(self.server_id, int(self.club_one_object.id))
        ladder_one.add_score(self.club_one_add_score, send_notify=False)
        ladder_one.add_log(self_log, send_notify=False)

        if isinstance(self.club_two_object, Club):
            # real club
            ladder_two = Ladder(self.server_id, int(self.club_two_object.id))
            ladder_two.add_log(target_log)

        # 发送通知
        if isinstance(self.club_two_object, Club):
            config = ConfigLadderRankReward.get_reward_object(final_club_two_order)
            n = Notification(self.server_id, int(self.club_two_object.id))
            n.add_ladder_notification(
                win=not self.club_one_win,
                from_name=self.club_one_object.name,
                current_order=final_club_two_order,
                ladder_score=config.reward_score,
            )

        ladder_match_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=int(self.club_one_object.id),
            target_id=self.club_two_object.id,
            win=self.club_one_win
        )
