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
from core.staff import StaffRecruit, StaffManger
# from core.training import TrainingExp, TrainingProperty, TrainingBroadcast, TrainingShop, TrainingSponsor
from core.item import ItemManager
from core.bag import Bag
from core.challenge import Challenge
from core.building import BuildingManager
from core.league.league import LeagueManger
from core.friend import FriendManager
from core.mail import MailManager
from core.task import TaskManager, RandomEvent
from core.chat import Chat
from core.notification import Notification
from core.ladder import Ladder, LadderStore
from core.statistics import FinanceStatistics
from core.sponsor import SponsorManager
from core.activity import ActivityCategory
from core.activity.login_reward import ActivityLoginReward
from core.activity.signin import SignIn
from core.active_value import ActiveValue
from core.training_match import TrainingMatch, TrainingMatchStore
# from core.elite_match import EliteMatch
from core.auction import AuctionManager
from core.system import send_broadcast_notify

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

    Bag(server_id, char_id).send_notify()

    StaffManger(server_id, char_id).send_notify()

    c.set_login()

    club = Club(server_id, char_id)
    club.send_notify()
    club.send_staff_slots_notify()

    StaffRecruit(server_id, char_id).send_notify()

    # TrainingExp(server_id, char_id).send_notify()
    # TrainingProperty(server_id, char_id).send_notify()
    # TrainingBroadcast(server_id, char_id).send_notify()
    # TrainingShop(server_id, char_id).send_notify()
    # TrainingSponsor(server_id, char_id).send_notify()

    ItemManager(server_id, char_id).send_notify()

    chall = Challenge(server_id, char_id)
    chall.send_chapter_notify()
    chall.send_challenge_notify()
    chall.energy_notify()


    BuildingManager(server_id, char_id).send_notify()
    LeagueManger(server_id, char_id).send_notify()
    FriendManager(server_id, char_id).send_notify()
    MailManager(server_id, char_id).send_notify()
    TaskManager(server_id, char_id).send_notify()
    RandomEvent(server_id, char_id).send_notify()

    Chat(server_id, char_id).send_notify()

    Notification(server_id, char_id).send_notify()

    Ladder(server_id, char_id).send_notify()
    LadderStore(server_id, char_id).send_notify()

    FinanceStatistics(server_id, char_id).send_notify()
    SponsorManager(server_id, char_id).send_notify()

    ActivityCategory(server_id, char_id).send_notify()
    ActivityLoginReward(server_id, char_id).send_notify()
    SignIn(server_id, char_id).send_notify()

    AuctionManager(server_id, char_id).send_bidding_list_notify()
    AuctionManager(server_id, char_id).send_sell_list_notify()

    av = ActiveValue(server_id, char_id)
    av.send_function_notify()
    av.send_value_notify()

    TrainingMatch(server_id, char_id).send_notify()
    TrainingMatchStore(server_id, char_id).send_notify()

    # em = EliteMatch(server_id, char_id)
    # em.elite_notify()

    send_broadcast_notify(char_id)

