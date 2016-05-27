# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 11:41
Description:

"""

from dianjing.exception import GameException

from core.abstract import AbstractClub, AbstractStaff
from core.mongo import MongoChallenge
from core.club import Club
from core.match import ClubMatch
from core.unit import NPCUnit
from core.task import TaskMain

from core.resource import ResourceClassification
from core.value_log import ValueLogChallengeMatchTimes, ValueLogAllChallengeWinTimes

from utils.message import MessagePipe
from utils.functional import make_string_id

from config import ConfigChapter, ConfigChallengeMatch, ConfigErrorMessage

from protomsg.challenge_pb2 import (
    ChallengeNotify,
    ChapterNotify,
    CHAPTER_REWARD_DONE,
    CHAPTER_REWARD_NOT,
    CHAPTER_REWARD_OK,
)

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


class ChallengeNPCStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, _id):
        super(ChallengeNPCStaff, self).__init__()

        self.id = make_string_id()
        self.oid = _id
        self.after_init()


class ChallengeNPCClub(AbstractClub):
    __slots__ = ['config']

    def __init__(self, challenge_match_id):
        super(ChallengeNPCClub, self).__init__()

        self.config = ConfigChallengeMatch.get(challenge_match_id)
        self.id = challenge_match_id

        self.name = self.config.name
        # TODO
        self.flag = 1

    def load_staffs(self, **kwargs):
        for position, _id, unit_id in self.config.staffs:
            s = ChallengeNPCStaff(_id)
            s.formation_position = position
            u = NPCUnit(unit_id, 0, 1)

            s.set_unit(u)
            s.calculate()
            self.formation_staffs.append(s)


INIT_CHALLENGE_IDS = []
for k, v in ConfigChallengeMatch.INSTANCES.iteritems():
    if not v.condition_challenge:
        INIT_CHALLENGE_IDS.append(k)


class Challenge(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoChallenge.exist(self.server_id, self.char_id):
            doc = MongoChallenge.document()
            doc['_id'] = self.char_id

            challenge_star = {}
            chapters = {}
            for i in INIT_CHALLENGE_IDS:
                challenge_star[str(i)] = 0
                chapters[str(ConfigChallengeMatch.get(i).chapter)] = {
                    'star': 0,
                    'rewards': [],
                }

            doc['challenge_star'] = challenge_star
            doc['chapters'] = chapters

            MongoChallenge.db(self.server_id).insert_one(doc)

    def current_challenge_id(self):
        # TODO
        return 0

    def get_today_times(self, challenge_id):
        today_times = ValueLogChallengeMatchTimes(self.server_id, self.char_id).count_of_today(sub_id=challenge_id)
        return today_times

    def start(self, challenge_id):
        config = ConfigChallengeMatch.get(challenge_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if config.condition_challenge:
            doc = MongoChallenge.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'challenge_star.{0}'.format(config.condition_challenge): 1}
            )

            if str(config.condition_challenge) not in doc['challenge_star']:
                raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_OPEN"))

        if self.get_today_times(challenge_id) >= config.times_limit:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_WITHOUT_TIMES"))

        club_one = Club(self.server_id, self.char_id)
        club_two = ChallengeNPCClub(challenge_id)
        match = ClubMatch(club_one, club_two)
        msg = match.start()
        msg.key = str(challenge_id)
        return msg

    def sweep(self, challenge_id):
        # 扫荡
        config = ConfigChallengeMatch.get(challenge_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            {
                'challenge_star.{0}'.format(challenge_id): 1,
                'challenge_drop.{0}'.format(challenge_id): 1,
            }
        )

        star = doc['challenge_star'].get(str(challenge_id), None)
        if star is None:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_OPEN"))
        if star != 3:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_3_STAR"))

        today_times = ValueLogChallengeMatchTimes(self.server_id, self.char_id).count_of_today(sub_id=challenge_id)
        remained_times = config.times_limit - today_times

        if remained_times > 5:
            sweep_times = 5
        else:
            sweep_times = remained_times

        drop_times = doc['challenge_drop'].get(str(challenge_id), {})
        drops = {}
        resource_classified_list = []
        for i in range(sweep_times):
            _drop = config.get_drop(drop_times)
            for _id, _amount in _drop:
                if _id in drops:
                    drops[_id] += _amount
                else:
                    drops[_id] = _amount

            resource_classified_list.append(ResourceClassification.classify(_drop))

        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'challenge_drop.{0}'.format(challenge_id): drop_times
            }}
        )

        ValueLogChallengeMatchTimes(self.server_id, self.char_id).record(sub_id=challenge_id, value=sweep_times)
        ValueLogAllChallengeWinTimes(self.server_id, self.char_id).record(value=sweep_times)

        resource_classified = ResourceClassification.classify(drops.items())
        resource_classified.add(self.server_id, self.char_id)

        self.send_challenge_notify(ids=[challenge_id])
        return resource_classified_list

    def report(self, key, star):
        challenge_id = int(key)
        config = ConfigChallengeMatch.get(challenge_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_EXIST"))

        ValueLogChallengeMatchTimes(self.server_id, self.char_id).record(sub_id=challenge_id)

        if star <= 0:
            return None

        ValueLogAllChallengeWinTimes(self.server_id, self.char_id).record()

        projection = {
            'challenge_star.{0}'.format(challenge_id): 1,
            'challenge_drop.{0}'.format(challenge_id): 1,
        }

        for i in config.next:
            projection['challenge_star.{0}'.format(i)] = 1
            chapter_id = ConfigChallengeMatch.get(i).chapter
            projection['chapters.{0}'.format(chapter_id)] = 1

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        updated_chapter_ids = []
        updated_challenge_ids = []

        old_star = doc['challenge_star'][str(challenge_id)]
        if star > old_star:
            MongoChallenge.db(self.server_id).update_one(
                {'_id': self.char_id},
                {
                    '$set': {'challenge_star.{0}'.format(challenge_id): star},
                    '$inc': {'chapters.{0}.star'.format(config.chapter): star - old_star}
                }
            )

            updated_chapter_ids.append(config.chapter)
            updated_challenge_ids.append(challenge_id)

            # open challenge, chapter
            for i in config.next:
                if str(i) in doc['challenge_star']:
                    continue

                updated_challenge_ids.append(i)

                MongoChallenge.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': {
                        'challenge_star.{0}'.format(i): 0,
                    }}
                )

                chapter_id = ConfigChallengeMatch.get(i).chapter
                if str(chapter_id) in doc['chapters']:
                    continue

                updated_chapter_ids.append(chapter_id)
                MongoChallenge.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': {
                        'chapters.{0}'.format(chapter_id): {
                            'star': 0,
                            'rewards': []
                        }
                    }}
                )

            self.send_chapter_notify(ids=updated_chapter_ids)
            self.send_challenge_notify(ids=updated_challenge_ids)

        # drop
        drop_times = doc['challenge_drop'].get(str(challenge_id), {})
        drop = config.get_drop(drop_times)

        resource_classified = ResourceClassification.classify(drop)
        resource_classified.add(self.server_id, self.char_id)

        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'challenge_drop.{0}'.format(challenge_id): drop_times
            }}
        )

        # task
        TaskMain(self.server_id, self.char_id).trig(challenge_id)

        return resource_classified

    def get_chapter_reward(self, chapter_id, index):
        config = ConfigChapter.get(chapter_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_CHAPTER_NOT_EXIST"))

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'chapters.{0}'.format(chapter_id): 1}
        )

        try:
            this_chapter = doc['chapters'][str(chapter_id)]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_CHAPTER_NOT_OPEN"))

        if index in this_chapter['rewards']:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_CHAPTER_HAS_ALREADY_REWARD"))

        try:
            need_star, item_id, item_amount = config.star_reward[index]
        except IndexError:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_CHAPTER_INVALID_REWARD"))

        if need_star > this_chapter['star']:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_CHAPTER_REWARD_STAR_NOT_ENOUGH"))

        resource_classified = ResourceClassification.classify([(item_id, item_amount)])
        resource_classified.add(self.server_id, self.char_id)

        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$push': {
                    'chapters.{0}.rewards'.format(chapter_id): index
                }
            }
        )

        self.send_chapter_notify(ids=[chapter_id])
        return resource_classified

    def send_chapter_notify(self, ids=None):
        if ids:
            act = ACT_UPDATE
            projection = {'chapters.{0}'.format(i): 1 for i in ids}
        else:
            act = ACT_INIT
            projection = {'chapters': 1}

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = ChapterNotify()
        notify.act = act
        for _id, _info in doc['chapters'].iteritems():
            star = _info['star']
            rewards = _info['rewards']

            notify_chapter = notify.chapters.add()
            notify_chapter.id = int(_id)

            config = ConfigChapter.get(int(_id))
            for index in range(len(config.star_reward)):
                notify_chapter_reward = notify_chapter.rewards.add()
                notify_chapter_reward.index = index

                if index in rewards:
                    notify_chapter_reward.status = CHAPTER_REWARD_DONE
                else:
                    need_star = config.star_reward[index][0]
                    if star >= need_star:
                        notify_chapter_reward.status = CHAPTER_REWARD_OK
                    else:
                        notify_chapter_reward.status = CHAPTER_REWARD_NOT

        MessagePipe(self.char_id).put(msg=notify)

    def send_challenge_notify(self, ids=None):
        if ids:
            act = ACT_UPDATE
            projection = {'challenge_star.{0}'.format(i): 1 for i in ids}
        else:
            act = ACT_INIT
            projection = {'challenge_star': 1}

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        ids = doc['challenge_star'].keys()

        times = ValueLogChallengeMatchTimes(self.server_id, self.char_id).batch_count_of_today()

        notify = ChallengeNotify()
        notify.act = act

        for i in ids:
            notify_challenge = notify.challenge.add()
            notify_challenge.id = int(i)
            notify_challenge.star = doc['challenge_star'][i]
            notify_challenge.remained_times = ConfigChallengeMatch.get(int(i)).times_limit - times.get(i, 0)

        MessagePipe(self.char_id).put(msg=notify)
