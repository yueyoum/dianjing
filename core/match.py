# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-05-21 15:08
Description:

"""

import base64
import random
import arrow

from dianjing.exception import GameException

from core.mongo import MongoMatchRecord
from utils.functional import make_string_id

from config import ConfigErrorMessage

from protomsg.match_pb2 import (
    ClubMatch as MessageClubMatch,
    ClubTroop as MessageClubTroop,
)


class ClubMatch(object):
    # 俱乐部比赛
    __slots__ = ['club_one', 'club_two', 'skill_sequence_amount', 'skill_sequence_one', 'skill_sequence_two', 'seed']

    def __init__(self, club_one, club_two, skill_sequence_amount, skill_sequence_one, skill_sequence_two):
        """

        :type club_one: core.abstract.AbstractClub | None
        :type club_two: core.abstract.AbstractClub | None
        """
        self.club_one = club_one
        self.club_two = club_two
        self.skill_sequence_amount = skill_sequence_amount
        self.skill_sequence_one = skill_sequence_one
        self.skill_sequence_two = skill_sequence_two
        self.seed = random.randint(1, 10000)

    def make_club_troop_msg(self, club_obj, skill_sequence):
        """

        :type club_obj: core.abstract.AbstractClub
        :type skill_sequence: dict[int, list]
        """
        from core.club import Club
        from core.bag import Bag, Equipment

        if isinstance(club_obj, Club):
            bag = Bag(club_obj.server_id, club_obj.char_id)
            slots = bag.doc['slots']
        else:
            slots = {}

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
                slot_data = slots.get(fs.equip_special, '')
                if slot_data:
                    equip = Equipment.load_from_slot_data(slot_data)
                    msg_troop.special_equipment_skills.extend(equip.get_active_skills_ids())

        for i in range(1, self.skill_sequence_amount+1):
            notify_skill_sequence = msg.skill_sequence.add()
            notify_skill_sequence.id = i
            notify_skill_sequence.staff_id.extend(skill_sequence.get(i, ["", "", ""]))

        return msg

    def start(self, auto_load_staffs=True, check_empty=True):
        if check_empty and self.club_one.power == 0:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if auto_load_staffs:
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
            msg.club_one.MergeFrom(self.make_club_troop_msg(self.club_one, self.skill_sequence_one))
        if self.club_two:
            msg.club_two.MergeFrom(self.make_club_troop_msg(self.club_two, self.skill_sequence_two))

        return msg


KEEP_DAYS = 30


class MatchRecord(object):
    __slots__ = ['server_id', 'id_one', 'id_two', 'club_match', 'record', 'create_at']

    @classmethod
    def clean(cls, server_id):
        now = arrow.utcnow().replace(days=-KEEP_DAYS)
        MongoMatchRecord.db(server_id).delete_many({'timestamp': {'$lte': now.timestamp}})

    @classmethod
    def get(cls, server_id, record_id):
        doc = MongoMatchRecord.db(server_id).find_one({'_id': record_id})
        if not doc:
            return None

        obj = cls()
        obj.server_id = server_id
        obj.id_one = doc['id_one']
        obj.id_two = doc['id_two']
        obj.club_match = base64.b64decode(doc['club_match'])
        obj.record = base64.b64decode(doc['record'])
        obj.create_at = doc['create_at']
        return obj

    @classmethod
    def create(cls, server_id, id_one, id_two, club_match, record=''):
        id_one = str(id_one)
        id_two = str(id_two)

        doc = cls._make_doc(id_one, id_two, club_match, record=record)
        MongoMatchRecord.db(server_id).insert_one(doc)
        return doc['_id']

    @classmethod
    def batch_create(cls, server_id, info_sets):
        docs = []
        record_ids = []

        for id_one, id_two, club_match, record in info_sets:
            id_one = str(id_one)
            id_two = str(id_two)

            doc = cls._make_doc(id_one, id_two, club_match, record=record)
            docs.append(doc)
            record_ids.append(doc['_id'])

        MongoMatchRecord.db(server_id).insert_many(docs)
        return record_ids

    @classmethod
    def _make_doc(cls, id_one, id_two, club_match, record=''):
        doc = MongoMatchRecord.document()
        doc['_id'] = make_string_id()
        doc['id_one'] = id_one
        doc['id_two'] = id_two
        doc['club_match'] = base64.b64encode(club_match)
        doc['record'] = base64.b64encode(record)
        doc['create_at'] = arrow.utcnow().timestamp
        return doc

    @classmethod
    def update_record(cls, server_id, record_id, record):
        MongoMatchRecord.db(server_id).update_one(
            {'_id': record_id},
            {'$set': {
                'record': base64.b64encode(record)
            }}
        )

    @classmethod
    def query_by_char_id(cls, server_id, char_id):
        pass
