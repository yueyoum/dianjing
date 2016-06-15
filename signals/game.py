# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2015-04-30 15:23
Description:

"""

import arrow
from django.dispatch import receiver

from core.signals import game_start_signal
from core.character import Character
from core.club import Club
from core.staff import StaffManger, StaffRecruit
from core.formation import Formation
from core.bag import Bag
from core.unit import UnitManager
from core.challenge import Challenge
from core.friend import FriendManager
from core.mail import MailManager
from core.task import RandomEvent, TaskMain, TaskDaily
from core.chat import Chat
from core.notification import Notification
from core.statistics import FinanceStatistics
from core.sponsor import SponsorManager
from core.activity import ActivityCategory
from core.activity.login_reward import ActivityLoginReward
from core.activity.signin import SignIn
from core.active_value import ActiveValue
from core.talent import TalentManager
# from core.auction import AuctionManager
from core.system import send_broadcast_notify
from core.dungeon import Dungeon
from core.arena import Arena
from core.tower import Tower
from core.territory import Territory, TerritoryStore, TerritoryFriend
from core.store import Store
from core.vip import VIP
from core.collection import Collection
from core.energy import Energy

from utils.message import MessagePipe
from protomsg.common_pb2 import UTCNotify


@receiver(game_start_signal, dispatch_uid='signals.game.game_start_handler')
def game_start_handler(server_id, char_id, **kwargs):
    MessagePipe(char_id).clean()

    msg = UTCNotify()
    msg.timestamp = arrow.utcnow().timestamp
    MessagePipe(char_id).put(msg=msg)

    c = Character(server_id, char_id)
    c.send_notify()

    UnitManager(server_id, char_id).send_notify()

    Bag(server_id, char_id).send_notify()

    StaffManger(server_id, char_id).send_notify()
    StaffRecruit(server_id, char_id).send_notify()
    Formation(server_id, char_id).send_notify()

    c.set_login()

    club = Club(server_id, char_id)
    club.send_notify()

    chall = Challenge(server_id, char_id)
    chall.send_chapter_notify()
    chall.send_challenge_notify()

    FriendManager(server_id, char_id).send_notify()
    MailManager(server_id, char_id).send_notify()

    RandomEvent(server_id, char_id).send_notify()
    TaskMain(server_id, char_id).send_notify()
    TaskDaily(server_id, char_id).send_notify()

    Chat(server_id, char_id).send_notify()

    Notification(server_id, char_id).send_notify()

    FinanceStatistics(server_id, char_id).send_notify()
    SponsorManager(server_id, char_id).send_notify()

    ActivityCategory(server_id, char_id).send_notify()
    ActivityLoginReward(server_id, char_id).send_notify()
    SignIn(server_id, char_id).send_notify()
    TalentManager(server_id, char_id).send_notify()

    Dungeon(server_id, char_id).send_notify()
    #
    # AuctionManager(server_id, char_id).send_bidding_list_notify()
    # AuctionManager(server_id, char_id).send_sell_list_notify()

    av = ActiveValue(server_id, char_id)
    av.send_function_notify()
    av.send_value_notify()

    a = Arena(server_id, char_id)
    a.send_notify()
    a.send_honor_notify()
    a.send_match_log_notify()

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

    send_broadcast_notify(char_id)
