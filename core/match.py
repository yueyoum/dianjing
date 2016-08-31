# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-05-21 15:08
Description:

"""

import random

from protomsg.match_pb2 import (
    ClubMatch as MessageClubMatch,
    ClubTroop as MessageClubTroop,
)


class ClubMatch(object):
    # 俱乐部比赛
    __slot__ = ['club_one', 'club_two']

    def __init__(self, club_one, club_two):
        """

        :type club_one: core.abstract.AbstractClub | None
        :type club_two: core.abstract.AbstractClub | None
        """
        self.club_one = club_one
        self.club_two = club_two
        self.seed = random.randint(1, 10000)

    @classmethod
    def make_club_troop_msg(cls, club_obj):
        """

        :type club_obj: core.abstract.AbstractClub
        """
        from core.bag import Bag, Equipment
        bag = Bag(club_obj.server_id, club_obj.char_id)

        msg = MessageClubTroop()
        msg.club.MergeFrom(club_obj.make_protomsg())

        for fs in club_obj.formation_staffs:
            if not fs.unit:
                continue

            msg_troop = msg.troop.add()
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
            msg_troop.hero.star = fs.star

            msg_troop.army.id = fs.unit.id
            msg_troop.army.hp = fs.unit.hp
            msg_troop.army.hpPercent = fs.unit.hp_percent
            msg_troop.army.attack = fs.unit.attack
            msg_troop.army.attackPercent = fs.unit.attack_percent
            msg_troop.army.defense = fs.unit.defense
            msg_troop.army.defensePercent = fs.unit.defense_percent
            msg_troop.army.attackSpeed = fs.unit.attack_speed
            msg_troop.army.attackSpeedPercent = fs.unit.attack_speed_percent
            msg_troop.army.attackDistance = fs.unit.attack_range
            msg_troop.army.attackDistancePercent = fs.unit.attack_range_percent
            msg_troop.army.moveSpeed = fs.unit.move_speed
            msg_troop.army.moveSpeedPercent = fs.unit.move_speed_percent
            msg_troop.army.hitRate = fs.unit.hit_rate
            msg_troop.army.dodgeRate = fs.unit.dodge_rate
            msg_troop.army.critRate = fs.unit.crit_rate
            msg_troop.army.critMulti = fs.unit.crit_multiple
            msg_troop.army.critAntiRate = fs.unit.toughness_rate

            msg_troop.army.appendAttackTerran = fs.unit.hurt_addition_to_terran
            msg_troop.army.appendAttackProtoss = fs.unit.hurt_addition_to_protoss
            msg_troop.army.appendAttackZerg = fs.unit.hurt_addition_to_zerg

            msg_troop.army.appendAttackedByTerran = fs.unit.hurt_addition_by_terran
            msg_troop.army.appendAttackedByProtoss = fs.unit.hurt_addition_by_protoss
            msg_troop.army.appendAttackedByZerg = fs.unit.hurt_addition_by_zerg

            msg_troop.army.finalHurtAppend = fs.unit.final_hurt_addition
            msg_troop.army.finalHurtReduce = fs.unit.final_hurt_reduce

            msg_troop.policy = fs.policy

            if fs.equip_special:
                equip = Equipment.load_from_slot_data(bag.get_slot(fs.equip_special))
                msg_troop.special_equipment_skills.extend(equip.get_active_skills_ids())

        return msg

    def start(self):
        if self.club_one and not self.club_one.formation_staffs:
            self.club_one.load_staffs()

        if self.club_two and not self.club_two.formation_staffs:
            self.club_two.load_staffs()

        if self.club_one and self.club_two:
            two_for_one_talents = self.club_two.get_talents_ids_for_rival()
            if two_for_one_talents:
                self.club_one.add_rival_talent_effects(two_for_one_talents)
                self.club_one.make_temporary_staff_calculate()

            one_for_two_talents = self.club_one.get_talents_ids_for_rival()
            if one_for_two_talents:
                self.club_two.add_rival_talent_effects(one_for_two_talents)
                self.club_two.make_temporary_staff_calculate()

        msg = MessageClubMatch()
        msg.seed = self.seed
        msg.key = ""

        if self.club_one:
            msg.club_one.MergeFrom(self.make_club_troop_msg(self.club_one))
        if self.club_two:
            msg.club_two.MergeFrom(self.make_club_troop_msg(self.club_two))

        return msg
