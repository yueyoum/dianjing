# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-05-21 15:08
Description:

"""

import random

from protomsg.match_pb2 import ClubMatch as MessageClubMatch


class ClubMatch(object):
    # 俱乐部比赛
    def __init__(self, club_one, club_two):
        """

        :type club_one: core.abstract.AbstractClub
        :type club_two: core.abstract.AbstractClub
        """
        self.club_one = club_one
        self.club_two = club_two
        self.seed = random.randint(1, 10000)

        self.club_one_fight_info = {}
        self.club_two_fight_info = {}
        self.club_one_winning_times = 0
        self.club_two_winning_times = 0

    @property
    def points(self):
        # 比分
        """

        :rtype : tuple
        """
        return self.club_one_winning_times, self.club_two_winning_times

    def start(self):
        if not self.club_one.formation_staffs:
            self.club_one.load_formation_staffs()
        if not self.club_two.formation_staffs:
            self.club_two.load_formation_staffs()

        msg = MessageClubMatch()
        msg.seed = self.seed
        msg.key = "this is key"

        def fill_club_msg(club_msg, club_obj):
            """
            :param club_msg:
            :type club_obj: core.abstract.AbstractClub
            """
            club_msg.club.MergeFrom(club_obj.make_protomsg())
            for fs in club_obj.formation_staffs:
                msg_troop = club_msg.troop.add()
                msg_troop.hero.id = fs.id
                msg_troop.hero.oid = fs.oid
                msg_troop.hero.position = fs.formation_position
                msg_troop.hero.attack = fs.attack
                msg_troop.hero.attackPercent = fs.attack_percent
                msg_troop.hero.defense = fs.defense
                msg_troop.hero.defensePercent = fs.defense_percent
                msg_troop.hero.manage = fs.manage
                msg_troop.hero.managePercent = fs.manage_percent
                msg_troop.hero.operation = fs.operation
                msg_troop.hero.operationPercent = fs.operation_percent

                msg_troop.army.id = fs.__unit.id
                msg_troop.army.hp = fs.__unit.hp
                msg_troop.army.hpPercent = fs.__unit.hp_percent
                msg_troop.army.attack = fs.__unit.attack
                msg_troop.army.attackPercent = fs.__unit.attack_percent
                msg_troop.army.defense = fs.__unit.defense
                msg_troop.army.defensePercent = fs.__unit.defense_percent
                msg_troop.army.attackSpeed = fs.__unit.attack_speed
                msg_troop.army.attackSpeedPercent = fs.__unit.attack_speed_percent
                msg_troop.army.attackDistance = fs.__unit.attack_range
                msg_troop.army.attackDistancePercent = fs.__unit.attack_range_percent
                msg_troop.army.moveSpeed = fs.__unit.move_speed
                msg_troop.army.moveSpeedPercent = fs.__unit.move_speed_percent
                msg_troop.army.hitRate = fs.__unit.hit_rate
                msg_troop.army.dodgeRate = fs.__unit.dodge_rate
                msg_troop.army.critRate = fs.__unit.crit_rate
                msg_troop.army.critMulti = fs.__unit.crit_multi
                msg_troop.army.critAntiRate = fs.__unit.toughness_rate

                msg_troop.army.appendAttackTerran = fs.__unit.hurt_addition_to_terran
                msg_troop.army.appendAttackProtoss = fs.__unit.hurt_addition_to_protoss
                msg_troop.army.appendAttackZerg = fs.__unit.hurt_addition_to_zerg

                msg_troop.army.appendAttackedByTerran = fs.__unit.hurt_addition_by_terran
                msg_troop.army.appendAttackedByProtoss = fs.__unit.hurt_addition_by_protoss
                msg_troop.army.appendAttackedByZerg = fs.__unit.hurt_addition_by_zerg

                msg_troop.army.finalHurtAppend = fs.__unit.final_hurt_addition
                msg_troop.army.finalHurtReduce = fs.__unit.final_hurt_reduce

        fill_club_msg(msg.club_one, self.club_one)
        fill_club_msg(msg.club_two, self.club_two)

        return msg
