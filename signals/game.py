# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2015-04-30 15:23
Description:

"""
import random

import arrow
from django.dispatch import receiver
from django.conf import settings

from core.signals import game_start_signal
from core.club import Club
from core.staff import StaffManger, StaffRecruit
from core.formation import Formation
from core.bag import Bag
from core.unit import UnitManager
from core.challenge import Challenge
from core.friend import FriendManager
from core.mail import MailManager
from core.task import TaskMain, TaskDaily
from core.chat import Chat
from core.notification import Notification
from core.statistics import FinanceStatistics
from core.talent import TalentManager
from core.system import send_system_notify, BroadCast
from core.dungeon import Dungeon
from core.arena import Arena
from core.tower import Tower
from core.territory import Territory, TerritoryStore, TerritoryFriend
from core.store import Store
from core.vip import VIP
from core.collection import Collection
from core.energy import Energy
from core.welfare import Welfare
from core.resource import _Resource
from core.union import Union
from core.purchase import Purchase
from core.activity import ActivityNewPlayer
from core.plunder import Plunder, SpecialEquipmentGenerator
from core.party import Party
from core.inspire import Inspire
from core.championship import Championship

from utils.message import MessagePipe
from utils.functional import days_passed

from protomsg.common_pb2 import UTCNotify, SocketServerNotify
from protomsg.club_pb2 import CreateDaysNotify


@receiver(game_start_signal, dispatch_uid='signals.game.game_start_handler')
def game_start_handler(server_id, char_id, **kwargs):
    MessagePipe(char_id).clean()

    msg = UTCNotify()
    msg.timestamp = arrow.utcnow().timestamp
    MessagePipe(char_id).put(msg=msg)

    club = Club(server_id, char_id)

    msg = CreateDaysNotify()
    msg.days = days_passed(club.create_at)
    msg.create_at = club.create_at
    MessagePipe(char_id).put(msg=msg)

    msg = SocketServerNotify()
    ss = random.choice(settings.SOCKET_SERVERS)
    msg.ip = ss['host']
    msg.port = ss['tcp']
    MessagePipe(char_id).put(msg=msg)

    _Resource.send_notify(server_id, char_id)

    UnitManager(server_id, char_id).send_notify()

    Bag(server_id, char_id).send_notify()

    StaffManger(server_id, char_id).send_notify()
    StaffRecruit(server_id, char_id).send_notify()

    f = Formation(server_id, char_id)
    f.send_formation_notify()
    f.send_slot_notify()

    club.set_login()
    club.send_notify()

    chall = Challenge(server_id, char_id)
    chall.send_chapter_notify()
    chall.send_challenge_notify()

    FriendManager(server_id, char_id).send_notify()
    MailManager(server_id, char_id).send_notify()

    TaskMain(server_id, char_id).send_notify()
    TaskDaily(server_id, char_id).send_notify()

    Chat(server_id, char_id).send_notify()

    Notification(server_id, char_id).send_notify()

    FinanceStatistics(server_id, char_id).send_notify()

    TalentManager(server_id, char_id).send_notify()

    Dungeon(server_id, char_id).send_notify()

    a = Arena(server_id, char_id)
    a.send_notify()
    a.send_honor_notify()

    t = Tower(server_id, char_id)
    t.send_notify()
    t.send_goods_notify()

    Territory(server_id, char_id).send_notify()
    TerritoryStore(server_id, char_id).send_notify()
    TerritoryFriend(server_id, char_id).send_remained_times_notify()

    Store(server_id, char_id).send_notify()
    VIP(server_id, char_id).send_notify()
    Collection(server_id, char_id).send_notify()

    Energy(server_id, char_id).send_notify()

    w = Welfare(server_id, char_id)
    w.send_signin_notify()
    w.send_new_player_notify()
    w.send_level_reward_notify()
    w.send_energy_reward_notify()

    u = Union(server_id, char_id)
    u.send_notify()
    u.send_my_check_notify()
    u.send_my_applied_notify()
    u.send_explore_notify()
    u.send_skill_notify()

    Purchase(server_id, char_id).send_notify()

    ac = ActivityNewPlayer(server_id, char_id)
    ac.send_notify()
    ac.send_daily_buy_notify()

    p = Plunder(server_id, char_id)

    p.send_search_notify()
    p.send_result_notify()
    p.send_revenge_notify()
    p.send_station_notify()
    p.send_formation_notify()
    p.send_plunder_times_notify()
    p.send_plunder_daily_reward_notify()

    SpecialEquipmentGenerator(server_id, char_id).send_notify()

    Party(server_id, char_id).send_notify()

    ins = Inspire(server_id, char_id)
    ins.try_open_slots(send_notify=False)
    ins.send_notify()

    cs = Championship(server_id, char_id)
    cs.try_initialize(send_notify=False)
    cs.send_notify()

    send_system_notify(server_id, char_id)
    BroadCast(server_id, char_id).try_cast_login_notify()
