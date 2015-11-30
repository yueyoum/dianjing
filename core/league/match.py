# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-11-10 15:53
Description:

"""

import random

from core.abstract import AbstractClub, AbstractStaff
from core.mongo import MongoLeagueGroup, MongoStaff, MongoCharacter
from core.club import Club
from core.mail import MailManager
from core.match import ClubMatch
from core.package import Drop
from core.signals import league_match_signal

from config import ConfigStaff, ConfigLeague, ConfigPolicy
from config.settings import (
    LEAGUE_DAY_WIN_MAIL_TITLE,
    LEAGUE_DAY_WIN_MAIL_CONTENT,
    LEAGUE_DAY_LOSE_MAIL_TITLE,
    LEAGUE_DAY_LOSE_MAIL_CONTENT,
    LEAGUE_WEEK_MAIL_TITLE,
    LEAGUE_WEEK_MAIL_CONTENT,
    LEAGUE_WIN_SCORE,
    LEAGUE_LOSE_SCORE,
)


class LeagueNPCStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, staff_attribute):
        super(LeagueNPCStaff, self).__init__()

        self.id = staff_attribute['id']
        config = ConfigStaff.get(self.id)

        self.level = 1
        self.race = config.race

        self.jingong = staff_attribute['jingong']
        self.qianzhi = staff_attribute['qianzhi']
        self.xintai = staff_attribute['xintai']
        self.baobing = staff_attribute['baobing']
        self.fangshou = staff_attribute['fangshou']
        self.yunying = staff_attribute['yunying']
        self.yishi = staff_attribute['yishi']
        self.caozuo = staff_attribute['caozuo']

        skill_level = staff_attribute.get('skill_level', 1)
        self.skills = {i: skill_level for i in config.skill_ids}


class LeagueBaseClubMixin(object):
    def __init__(self, league_level, club):
        self.league_level = league_level
        self.match_times = club['match_times']
        self.win_times = club['win_times']
        self.score = club['score']
        self.score_change = 0
        self.got_gold = 0

    def send_mail(self, win):
        # 每次打完后发
        config = ConfigLeague.get(self.league_level)

        if win:
            title = LEAGUE_DAY_WIN_MAIL_TITLE
            content = LEAGUE_DAY_WIN_MAIL_CONTENT
            package_id = config.day_reward
        else:
            title = LEAGUE_DAY_LOSE_MAIL_TITLE
            content = LEAGUE_DAY_LOSE_MAIL_CONTENT
            package_id = config.day_reward_lose

        drop = Drop.generate(package_id)
        self.got_gold += drop.gold

        self.do_send_mail(title, content, drop.to_json())

    def do_send_mail(self, title, content, attachment):
        raise NotImplementedError()

    def send_week_mail(self):
        pass

    def get_staff_winning_rate(self, staff_ids=None):
        raise NotImplementedError()

    def get_match_staffs_winning_rate(self):
        raise NotImplementedError()

    def save_winning_rate(self, fight_info):
        """

        :type fight_info: dict[int, core.match.FightInfo]
        """
        raise NotImplementedError()

    def set_times_and_score(self, win):
        self.match_times += 1
        if win:
            self.win_times += 1

            self.score += LEAGUE_WIN_SCORE
            self.score_change += LEAGUE_WIN_SCORE
        else:
            self.score += LEAGUE_LOSE_SCORE
            self.score_change += LEAGUE_LOSE_SCORE

    def league_level_up(self):
        pass


class LeagueNPCClub(LeagueBaseClubMixin, AbstractClub):
    def __init__(self, server_id, group_id, league_level, club):
        LeagueBaseClubMixin.__init__(self, league_level, club)
        AbstractClub.__init__(self)

        self.id = '{0}:{1}'.format(group_id, club['club_id'])
        self.name = club['club_name']
        self.manager_name = club['manager_name']
        self.flag = club['club_flag']
        self.server_id = server_id
        self.policy = random.choice(ConfigPolicy.INSTANCES.keys())

        for s in club['staffs']:
            self.match_staffs.append(s['id'])
            self.staffs[s['id']] = LeagueNPCStaff(s)

        self.qianban_affect()

    def do_send_mail(self, title, content, attachment):
        pass

    def get_match_staffs_winning_rate(self):
        group_id, club_id = self.id.split(':')
        data = MongoLeagueGroup.db(self.server_id).find_one(
            {'_id': group_id},
            {'clubs.{0}.staff_winning_rate'.format(club_id): 1}
        )
        club = data['clubs'][club_id]

        rate = {}
        for s in self.match_staffs:
            race_rate = {
                '1': 0,
                '2': 0,
                '3': 0,
            }

            staff_winning_info = club.get('staff_winning_rate', {}).get(str(s), {})
            for race, info in staff_winning_info.iteritems():
                race_rate[str(race)] = info.get('win', 0) * 100 / info['total']

            # rate格式 { staff_id:{'1':x, '2':x, '3':x}, ...}
            rate[s] = race_rate
        return rate

    def save_winning_rate(self, fight_info):
        """

        :type fight_info: dict[int, core.match.FightInfo]
        """
        group_id, club_id = self.id.split(':')

        updater = {}
        for staff_id, info in fight_info.iteritems():
            config_rival = ConfigStaff.get(info.rival)
            updater['clubs.{0}.staff_winning_rate.{1}.{2}.total'.format(club_id, staff_id, config_rival.race)] = 1
            if info.win:
                updater['clubs.{0}.staff_winning_rate.{1}.{2}.win'.format(club_id, staff_id, config_rival.race)] = 1

        MongoLeagueGroup.db(self.server_id).update_one(
            {'_id': group_id},
            {'$inc': updater}
        )


class LeagueRealClub(LeagueBaseClubMixin, Club):
    def __init__(self, server_id, league_level, club):
        LeagueBaseClubMixin.__init__(self, league_level, club)
        Club.__init__(self, server_id, int(club['club_id']))

    def do_send_mail(self, title, content, attachment):
        m = MailManager(self.server_id, self.char_id)
        m.add(title, content, attachment=attachment)

    def send_week_mail(self):
        config = ConfigLeague.get(self.league_level)
        drop = Drop.generate(config.week_reward)
        attachment = drop.to_json()

        m = MailManager(self.server_id, self.char_id)
        m.add(LEAGUE_WEEK_MAIL_TITLE, LEAGUE_WEEK_MAIL_CONTENT, attachment=attachment)

    def get_staff_winning_rate(self, staff_ids=None):
        if staff_ids:
            projection = {'staffs.{0}'.format(s): 1 for s in staff_ids}
        else:
            projection = {'staffs': 1}

        data = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        staffs = data['staffs']

        rate = {}
        for s in staffs:
            race_rate = {
                '1': 0,
                '2': 0,
                '3': 0,
            }
            winning_rate = staffs[s].get('winning_rate', {})
            for race, info in winning_rate.iteritems():
                race_rate[str(race)] = info.get('win', 0) * 100 / info['total']

            # example: rate ={91: {'1':0.333, '2':0.555, '3': 0.9},  ... ]
            rate[int(s)] = race_rate
        return rate

    def get_match_staffs_winning_rate(self):
        return self.get_staff_winning_rate(staff_ids=self.match_staffs)

    def save_winning_rate(self, fight_info):
        """

        :type fight_info: dict[int, core.match.FightInfo]
        """
        updater = {}
        for k, v in fight_info.iteritems():
            config_rival = ConfigStaff.get(v.rival)
            updater['staffs.{0}.winning_rate.{1}.total'.format(k, config_rival.race)] = 1
            if v.win:
                updater['staffs.{0}.winning_rate.{1}.win'.format(k, config_rival.race)] = 1

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': updater}
        )

    def league_level_up(self):
        if self.league_level >= ConfigLeague.MAX_LEVEL:
            return

        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'league_level': 1
            }}
        )


class LeagueClub(object):
    def __new__(cls, server_id, group_id, league_level, club):
        # club 是存在mongo中的数据
        if club['club_name']:
            return LeagueNPCClub(server_id, group_id, league_level, club)

        return LeagueRealClub(server_id, league_level, club)


class LeagueMatch(object):
    # 一对俱乐部比赛
    def __init__(self, server_id, club_one_object, club_two_object):
        """

        :type club_one_object: LeagueNPCClub | LeagueRealClub
        :type club_two_object: LeagueNPCClub | LeagueRealClub
        """
        self.server_id = server_id

        self.club_one_object = club_one_object
        self.club_two_object = club_two_object

        self.club_one_win = False
        self.points = (0, 0)

    def start(self):

        match = ClubMatch(self.club_one_object, self.club_two_object)
        msg = match.start()
        self.club_one_win = msg.club_one_win
        self.points = match.points

        self.club_one_object.save_winning_rate(match.get_club_one_fight_info())
        self.club_two_object.save_winning_rate(match.get_club_two_fight_info())

        self.after_match()
        return msg

    def after_match(self):
        # 记录 times, score
        self.club_one_object.set_times_and_score(self.club_one_win)
        self.club_two_object.set_times_and_score(not self.club_one_win)

        # 发送邮件
        self.club_one_object.send_mail(self.club_one_win)
        self.club_two_object.send_mail(not self.club_one_win)

        if isinstance(self.club_one_object, Club):
            league_match_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=int(self.club_one_object.id),
                target_id=self.club_two_object.id,
                win=self.club_one_win
            )

        if isinstance(self.club_two_object, Club):
            league_match_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=int(self.club_two_object.id),
                target_id=self.club_one_object.id,
                win=not self.club_one_win
            )
