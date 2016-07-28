# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       union
Date Created:   2016-07-27 15:04
Description:

"""
from collections import OrderedDict

import arrow
from pymongo.errors import DuplicateKeyError

from dianjing.exception import GameException

from core.mongo import MongoUnion, MongoUnionMember
from core.resource import ResourceClassification, money_text_to_item_id
from core.value_log import ValueLogUnionSignInTimes
from core.club import Club
from core.vip import VIP

from utils.message import MessagePipe
from utils.functional import make_string_id

from config import GlobalConfig, ConfigErrorMessage, ConfigUnionSignin, ConfigUnionLevel

from protomsg.union_pb2 import UnionMyAppliedNotify, UnionMyCheckNotify, UnionNotify, UnionMember as MsgMember

BULLETIN_MAX_LENGTH = 255


class _UnionInfo(object):
    __slots__ = ['server_id', 'id', 'name', 'owner', 'level', 'contribution', 'rank']

    def __init__(self, server_id, doc):
        self.server_id = server_id

        self.id = doc['_id']
        self.name = doc['name']
        self.owner = doc['owner']
        self.level = doc['level']
        self.contribution = doc['contribution']

        self.rank = None

    @property
    def members_amount(self):
        return MongoUnionMember.db(self.server_id).find({'joined': self.id}).count()

    @property
    def all_contribution(self):
        contribution = self.contribution
        for lv in range(self.level - 1, 0, -1):
            contribution += ConfigUnionLevel.get(lv).contribution

        return contribution


def get_all_unions(server_id):
    """

    :rtype: dict[str, _UnionInfo]
    """
    docs = MongoUnion.db(server_id).find({}, {'create_at': 0, 'bulletin': 0, 'apply_list': 0})

    unions = []
    for doc in docs:
        unions.append(_UnionInfo(server_id, doc))

    unions.sort(key=lambda item: item.all_contribution, reverse=True)

    res = OrderedDict()
    for index, u in enumerate(unions):
        u.rank = index + 1
        res[u.id] = u

    return res


class _MemberClub(Club):
    __slots__ = ['contribution', 'today_contribution']

    def __init__(self, server_id, char_id, contribution, today_contribution):
        super(_MemberClub, self).__init__(server_id, char_id)
        self.contribution = contribution
        self.today_contribution = today_contribution

    def make_member_protomsg(self):
        msg = MsgMember()
        msg.id = str(self.id)
        msg.flag = self.flag
        msg.name = self.name
        msg.level = self.level
        msg.power = self.power
        msg.total_contribution = self.contribution
        msg.today_contribution = self.today_contribution

        return msg


class Union(object):
    def __new__(cls, server_id, char_id):
        """

        :rtype: IUnion
        """
        member_doc = MongoUnionMember.db(server_id).find_one({'_id': char_id})
        if not member_doc:
            member_doc = MongoUnionMember.document()
            member_doc['_id'] = char_id
            MongoUnionMember.db(server_id).insert_one(member_doc)

        if not member_doc['joined']:
            return UnionNotJoined(server_id, char_id, None, None)

        union_doc = MongoUnion.db(server_id).find_one({'_id': member_doc['joined']})
        if union_doc['owner'] == char_id:
            return UnionOwner(server_id, char_id, member_doc, union_doc)

        return UnionMember(server_id, char_id, member_doc, union_doc)


class IUnion(object):
    __slots__ = ['server_id', 'char_id', 'member_doc', 'union_doc']

    def __init__(self, server_id, char_id, member_doc, union_doc):
        self.server_id = server_id
        self.char_id = char_id
        self.member_doc = member_doc
        self.union_doc = union_doc

    def create(self, name):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def apply_union(self, union_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def set_bulletin(self, content):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def agree(self, char_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def refuse(self, char_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def kick(self, char_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def transfer(self, char_id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def quit(self):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def sign_in(self, _id):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def check_level(self, target_level):
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    def send_notify(self, **kwargs):
        raise NotImplementedError()

    def send_my_applied_notify(self):
        raise NotImplementedError()

    def send_my_check_notify(self):
        raise NotImplementedError()


# 没有加入公会
class UnionNotJoined(IUnion):
    __slots__ = []

    def create(self, name):
        cost = [(money_text_to_item_id('diamond'), GlobalConfig.value("UNION_CREATE_COST"))]
        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)

        doc = MongoUnion.document()
        doc['_id'] = make_string_id()
        doc['create_at'] = arrow.utcnow().timestamp
        doc['name'] = name
        doc['owner'] = self.char_id

        try:
            MongoUnion.db(self.server_id).insert_one(doc)
        except DuplicateKeyError:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_NAME_HAS_TAKEN"))

        MongoUnionMember.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'joined': doc['_id'],
                'joined_at': arrow.utcnow().timestamp
            }}
        )

        u = Union(self.server_id, self.char_id)
        u.send_notify()
        u.send_my_applied_notify()

    def apply_union(self, union_id):
        doc = MongoUnion.db(self.server_id).find_one({'_id': union_id})
        if not doc:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_NOT_EXIST"))

        config = ConfigUnionLevel.get(doc['level'])

        if MongoUnionMember.db(self.server_id).find({'joined': union_id}).count() >= config.members_limit:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_CANNOT_APPLY_MEMBERS_LIMIT"))

        MongoUnion.db(self.server_id).update_one(
            {'_id': union_id},
            {'$addToSet': {
                'apply_list': self.char_id
            }}
        )

        self.send_my_applied_notify()

        u = Union(self.server_id, doc['owner'])
        u.send_my_check_notify()


    def send_notify(self):
        notify = UnionNotify()
        notify.id = ""
        notify.name = ""
        notify.bulletin = ""
        notify.level = 0
        notify.contribution = 0
        notify.rank = 0
        notify.my_contribution = 0
        notify.signin_id = 0
        MessagePipe(self.char_id).put(msg=notify)

    def send_my_applied_notify(self):
        docs = MongoUnion.db(self.server_id).find({'apply_list': self.char_id}, {'_id': 1})
        ids = [d['_id'] for d in docs]

        notify = UnionMyAppliedNotify()
        notify.union_ids.extend(ids)
        MessagePipe(self.char_id).put(msg=notify)

    def send_my_check_notify(self):
        pass


class UnionJoined(IUnion):
    __slots__ = []

    def create(self, name):
        raise GameException(ConfigErrorMessage.get_error_id("UNION_CANNOT_CREATE_ALREADY_IN"))

    def apply_union(self, union_id):
        raise GameException(ConfigErrorMessage.get_error_id("UNION_CANNOT_APPLY_ALREADY_IN"))

    def quit(self, send_notify=True):
        self.member_doc['joined'] = 0
        self.member_doc['joined_at'] = 0
        self.member_doc['contribution'] = 0
        self.member_doc['today_contribution'] = 0

        MongoUnionMember.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'joined': 0,
                'joined_at': 0,
                'contribution': 0,
                'today_contribution': 0,
            }}
        )

        if send_notify:
            self.send_notify_to_all_members()

    def sign_in(self, _id):
        """

        :rtype: ResourceClassification
        """
        if self.get_signed_id():
            raise GameException(ConfigErrorMessage.get_error_id("UNION_ALREADY_SIGNED"))

        config = ConfigUnionSignin.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if config.vip:
            VIP(self.server_id, self.char_id).check(config.vip)

        rc = ResourceClassification.classify(config.cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id)

        self.add_contribution(config.contribution, send_notify=False)

        rc = ResourceClassification.classify(config.rewards)
        rc.add(self.server_id, self.char_id)

        ValueLogUnionSignInTimes(self.server_id, self.char_id).record(sub_id=_id)

        self.send_notify()
        return rc

    def check_level(self, target_level):
        if self.union_doc['level'] < target_level:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_LEVEL_NOT_ENOUGH"))

    def add_contribution(self, value, send_notify=True):
        # 给自己加
        MongoUnionMember.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'contribution': value,
                'today_contribution': value
            }}
        )

        self.member_doc = MongoUnionMember.db(self.server_id).find_one({'_id': self.char_id})

        # 给公会加
        union_contribution = self.union_doc['contribution'] + value
        level = self.union_doc['level']

        while True:
            if level >= ConfigUnionLevel.MAX_LEVEL:
                level = ConfigUnionLevel.MAX_LEVEL

                if union_contribution >= ConfigUnionLevel.get(ConfigUnionLevel.MAX_LEVEL).contribution:
                    union_contribution = ConfigUnionLevel.get(ConfigUnionLevel.MAX_LEVEL).contribution

                break

            up_need = ConfigUnionLevel.get(level).contribution
            if union_contribution < up_need:
                break

            union_contribution -= up_need
            level += 1

        self.union_doc['level'] = level
        self.union_doc['contribution'] = union_contribution

        MongoUnion.db(self.server_id).update_one(
            {'_id': self.union_doc['_id']},
            {'$set': {
                'level': level,
                'contribution': union_contribution
            }}
        )

        if send_notify:
            self.send_notify()

    def get_signed_id(self):
        times = ValueLogUnionSignInTimes(self.server_id, self.char_id).batch_count_of_today()
        if not times:
            return 0

        _id = times.keys()[0]
        return int(_id)

    def get_members(self):
        """

        :rtype: list[_MemberClub]
        """
        owner = self.union_doc['owner']
        docs = MongoUnionMember.db(self.server_id).find({'joined': self.union_doc['_id']})

        owner_doc = None
        members = []
        for doc in docs:
            if doc['_id'] == owner:
                owner_doc = doc
                continue

            members.append(_MemberClub(self.server_id, doc['_id'], doc['contribution'], doc['today_contribution']))

        members.sort(key=lambda item: item.contribution, reverse=True)

        members.insert(0, _MemberClub(self.server_id, owner_doc['_id'], owner_doc['contribution'],
                                      owner_doc['today_contribution']))
        return members

    def get_members_amount(self):
        return MongoUnionMember.db(self.server_id).find({'joined': self.union_doc['_id']}).count()

    def get_rank(self):
        unions = get_all_unions(self.server_id)
        return unions[self.union_doc['_id']].rank

    def send_notify_to_all_members(self, rank=None, send_my_check_notify=False):
        if rank is None:
            rank = self.get_rank()

        for doc in MongoUnionMember.db(self.server_id).find({'joined': self.union_doc['_id']}):
            u = Union(self.server_id, doc['_id'])
            u.send_notify(rank=rank)
            if send_my_check_notify:
                u.send_my_check_notify()

    def send_notify(self, rank=None):
        notify = UnionNotify()
        notify.id = self.union_doc['_id']
        notify.name = self.union_doc['name']
        notify.bulletin = self.union_doc['bulletin']
        notify.level = self.union_doc['level']
        notify.contribution = self.union_doc['contribution']

        if rank is None:
            rank = self.get_rank()
        notify.rank = rank
        notify.my_contribution = self.member_doc['contribution']

        members = self.get_members()
        for m in members:
            notify_member = notify.members.add()
            notify_member.MergeFrom(m.make_member_protomsg())

        notify.signin_id = self.get_signed_id()

        MessagePipe(self.char_id).put(msg=notify)

    def send_my_applied_notify(self):
        notify = UnionMyAppliedNotify()
        MessagePipe(self.char_id).put(msg=notify)


# 普通公会成员
class UnionMember(UnionJoined):
    __slots__ = []

    def send_my_check_notify(self):
        notify = UnionMyCheckNotify()
        MessagePipe(self.char_id).put(msg=notify)


# 会长
class UnionOwner(UnionJoined):
    __slots__ = []

    def set_bulletin(self, content):
        if len(content) > BULLETIN_MAX_LENGTH:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_BULLETIN_TOO_LONG"))

        self.union_doc['bulletin'] = content
        MongoUnion.db(self.server_id).update_one(
            {'_id': self.union_doc['_id']},
            {'$set': {
                'bulletin': content
            }}
        )

        self.send_notify_to_all_members()

    def agree(self, char_id):
        if char_id not in self.union_doc['apply_list']:
            self.send_my_check_notify()
            raise GameException(ConfigErrorMessage.get_error_id("UNION_TARGET_ALREADY_JOIN_A_UNION"))

        self.union_doc['apply_list'].remove(char_id)
        MongoUnion.db(self.server_id).update_many(
            {'apply_list': char_id},
            {'$pull': {
                'apply_list': char_id
            }}
        )

        self.send_my_check_notify()

        if self.get_members_amount() >= ConfigUnionLevel.get(self.union_doc['level']).members_limit:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_MEMBERS_REACH_LIMIT"))

        u = Union(self.server_id, char_id)
        if isinstance(u, UnionJoined):
            raise GameException(ConfigErrorMessage.get_error_id("UNION_TARGET_ALREADY_JOIN_A_UNION"))

        MongoUnionMember.db(self.server_id).update_one(
            {'_id': char_id},
            {'$set': {
                'joined': self.union_doc['_id'],
                'joined_at': arrow.utcnow().timestamp
            }}
        )

        self.send_notify()

        u = Union(self.server_id, char_id)
        u.send_notify()
        u.send_my_applied_notify()

    def refuse(self, char_id):
        try:
            self.union_doc['apply_list'].remove(char_id)
        except ValueError:
            pass

        MongoUnion.db(self.server_id).update_one(
            {'_id': self.union_doc['_id']},
            {'$pull': {
                'apply_list': char_id
            }}
        )

        self.send_my_check_notify()
        Union(self.server_id, char_id).send_my_applied_notify()

    def kick(self, char_id):
        if char_id == self.char_id:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        u = Union(self.server_id, char_id)
        if not isinstance(u, UnionMember) or u.member_doc['joined'] != self.union_doc['_id']:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_TARGET_NOT_MEMBER"))

        u.quit()

    def transfer(self, char_id):
        if char_id == self.char_id:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        u = Union(self.server_id, char_id)
        if not isinstance(u, UnionMember) or u.member_doc['joined'] != self.union_doc['_id']:
            raise GameException(ConfigErrorMessage.get_error_id("UNION_TARGET_NOT_MEMBER"))

        self.union_doc['owner'] = char_id
        MongoUnion.db(self.server_id).update_one(
            {'_id': self.union_doc['_id']},
            {'$set': {
                'owner': char_id
            }}
        )

        self.send_notify_to_all_members(send_my_check_notify=True)

    def quit(self, *args):
        super(UnionOwner, self).quit(send_notify=False)
        if self.get_members_amount() == 0:
            MongoUnion.db(self.server_id).delete_one({'_id': self.union_doc['_id']})

        members = self.get_members()
        next_char_id = members[1].char_id
        self.transfer(next_char_id)

    def send_my_check_notify(self):
        notify = UnionMyCheckNotify()

        for cid in self.union_doc['apply_list']:
            m = _MemberClub(self.server_id, cid, 0, 0)
            notify_member = notify.members.add()
            notify_member.MergeFrom(m.make_member_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
