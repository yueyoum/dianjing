# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-05-21 15:08
Description:

"""

import random
from dianjing.exception import GameException
from config import ConfigErrorMessage, ConfigStaffNew, ConfigUnitNew

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

        # if not self.club_one.match_staffs_ready() or not self.club_two.match_staffs_ready():
        #     raise GameException(ConfigErrorMessage.get_error_id("MATCH_STAFF_NOT_READY"))

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
        msg = MessageClubMatch()
        msg.seed = self.seed
        msg.key = "this is key"

        def fill_club_msg(club_msg, club_obj):
            """

            :type club_obj: core.abstract.AbstractClub
            """
            club_msg.club.MergeFrom(club_obj.make_protomsg())
            for i in club_obj.match_staffs:
                # TODO 现在是直接从config获取 staff, unit的数据
                # 需要改成 Staff, Unit 类，它们包含了这些数据
                staff_obj = club_obj.staffs[i]
                config_staff_new = ConfigStaffNew.get(i)
                config_unit_new = ConfigUnitNew.get(staff_obj.unit_id)

                msg_troop = club_msg.troop.add()
                msg_troop.hero.id = i
                msg_troop.hero.position = staff_obj.position
                msg_troop.hero.attack = config_staff_new.attack
                msg_troop.hero.attackPercent = 0
                msg_troop.hero.defense = config_staff_new.defense
                msg_troop.hero.defensePercent = 0
                msg_troop.hero.manage = config_staff_new.manage
                msg_troop.hero.managePercent = 0
                msg_troop.hero.operation = config_staff_new.cost
                msg_troop.hero.operationPercent = 0

                msg_troop.army.id = staff_obj.unit_id
                msg_troop.army.hp = config_unit_new.hp_max_base
                msg_troop.army.hpPercent = 0
                msg_troop.army.attack = config_unit_new.attack_base
                msg_troop.army.attackPercent = 0
                msg_troop.army.defense = config_unit_new.defense_base
                msg_troop.army.defensePercent = 0
                msg_troop.army.attackSpeed = config_unit_new.attack_speed_base
                msg_troop.army.attackSpeedPercent = 0
                msg_troop.army.attackDistance = config_unit_new.attack_range_base
                msg_troop.army.attackDistancePercent = 0
                msg_troop.army.moveSpeed = config_unit_new.move_speed_base
                msg_troop.army.moveSpeedPercent = 0
                msg_troop.army.hitRate = config_unit_new.hit_rate
                msg_troop.army.dodgeRate = config_unit_new.dodge_rate
                msg_troop.army.critRate = config_unit_new.crit_rate
                msg_troop.army.critMulti = config_unit_new.crit_multiple
                msg_troop.army.critAntiRate = config_unit_new.toughness_rate

                msg_troop.army.appendAttackTerrn = config_unit_new.hurt_addition_to_terran
                msg_troop.army.appendAttackProtoss = config_unit_new.hurt_addition_to_protoss
                msg_troop.army.appendAttackZerg = config_unit_new.hurt_addition_to_zerg

                msg_troop.army.appendAttackedByTerrn = config_unit_new.hurt_addition_by_terran
                msg_troop.army.appendAttackedByProtoss = config_unit_new.hurt_addition_by_protoss
                msg_troop.army.appendAttackedByZerg = config_unit_new.hurt_addition_by_zerg

                msg_troop.army.finalHurtAppend = config_unit_new.final_hurt_addition
                msg_troop.army.finalHurtReduce = config_unit_new.final_hurt_reduce

        fill_club_msg(msg.club_one, self.club_one)
        fill_club_msg(msg.club_two, self.club_two)

        return msg
