# # -*- coding: utf-8 -*-
# """
# Author:         Wang Chao <yueyoum@gmail.com>
# Filename:       group
# Date Created:   2015-11-10 15:19
# Description:
#
# """
#
# # from core.mongo import MongoCharacter, MongoLeagueGroup, MongoLeagueEvent
#
# from config import ConfigNPC
#
# from utils.functional import make_string_id
#
# GROUP_CLUBS_AMOUNT = 14
# GROUP_MAX_REAL_CLUBS_AMOUNT = 12
#
#
# def arrange_match(clubs):
#     # 对小组内的14支俱乐部安排比赛
#     # 算法：
#     match = []
#     pairs = []
#     for i in [0, 1]:
#         for interval in range(1, 14, 2):
#             for j in range(0, 13, 2):
#                 a = i + j
#                 b = a + interval
#                 if b > 13:
#                     b -= 14
#
#                 p = (clubs[a], clubs[b])
#                 pairs.append(p)
#
#     while pairs:
#         match.append(pairs[:7])
#         pairs = pairs[7:]
#
#     return match
#
#
# class LeagueGroup(object):
#     __slots__ = ['id', 'server_id', 'level', 'real_clubs', 'all_clubs', 'event_docs']
#
#     class AddFinish(Exception):
#         pass
#
#     def __init__(self, server_id, level):
#         self.id = make_string_id()
#
#         self.server_id = server_id
#         self.level = level
#
#         # 记录real club的id列表
#         self.real_clubs = []
#         # 所有clubs  id: data
#         self.all_clubs = {}
#
#         self.event_docs = []
#
#     @property
#     def event_ids(self):
#         return [e['_id'] for e in self.event_docs]
#
#     def add(self, club_id):
#         self.real_clubs.append(club_id)
#
#         if len(self.real_clubs) >= GROUP_MAX_REAL_CLUBS_AMOUNT:
#             raise LeagueGroup.AddFinish()
#
#     def finish(self):
#         if not self.real_clubs:
#             return
#
#         def make_real_club_doc(club_id):
#             doc = MongoLeagueGroup.document_embedded_club()
#             doc['club_id'] = str(club_id)
#             return doc
#
#         def make_npc_club_doc(n):
#             doc = MongoLeagueGroup.document_embedded_club()
#             doc['club_id'] = make_string_id()
#             doc['club_name'] = n['club_name']
#             doc['manager_name'] = n['manager_name']
#             doc['club_flag'] = n['club_flag']
#             doc['staffs'] = n['staffs']
#             return doc
#
#         clubs = [make_real_club_doc(i) for i in self.real_clubs]
#
#         need_npc_amount = GROUP_CLUBS_AMOUNT - len(clubs)
#         npcs = ConfigNPC.random_npcs(need_npc_amount, league_level=self.level)
#
#         npc_clubs = [make_npc_club_doc(npc) for npc in npcs]
#
#         clubs.extend(npc_clubs)
#         self.all_clubs = {str(c['club_id']): c for c in clubs}
#
#         match = arrange_match(self.all_clubs.keys())
#         self.save(match)
#
#     def save(self, match):
#         from core.league.league import LeagueGame
#
#         def make_pair_doc(club_one, club_two):
#             doc = MongoLeagueEvent.document_embedded_pair()
#             doc['club_one'] = club_one
#             doc['club_two'] = club_two
#             return doc
#
#         for index, event in enumerate(match):
#             event_doc = MongoLeagueEvent.document()
#             event_doc['_id'] = make_string_id()
#             event_doc['start_at'] = LeagueGame.find_match_time(index + 1).timestamp
#
#             pair_docs = [make_pair_doc(one, two) for one, two in event]
#             event_doc['pairs'] = {str(i + 1): pair_docs[i] for i in range(len(pair_docs))}
#
#             self.event_docs.append(event_doc)
#
#         group_doc = MongoLeagueGroup.document()
#         group_doc['_id'] = self.id
#         group_doc['level'] = self.level
#         group_doc['clubs'] = self.all_clubs
#         group_doc['events'] = self.event_ids
#
#         MongoLeagueEvent.db(self.server_id).insert_many(self.event_docs)
#         MongoLeagueGroup.db(self.server_id).insert_one(group_doc)
#
#         # 然后将 此 group_id 关联到 character中
#         MongoCharacter.db(self.server_id).update_many(
#             {'_id': {'$in': self.real_clubs}},
#             {'$set': {'league_group': self.id}}
#         )
