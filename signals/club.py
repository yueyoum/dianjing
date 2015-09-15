# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-23 18:31
Description:

"""

from core.mongo import MongoCharacter
from core.signals import match_staffs_set_done_signal
from core.league import LeagueGame

def match_staffs_set_done(server_id, char_id, match_staffs, **kwargs):
    doc = MongoCharacter.db(server_id).find_one({'_id': char_id}, {'league_group': 1})
    group_id = doc.get('league_group', "")
    if not group_id:
        LeagueGame.join_already_started_league(server_id, char_id)


match_staffs_set_done_signal.connect(
    match_staffs_set_done,
    dispatch_uid='signals.club.match_staffs_set_done'
)
