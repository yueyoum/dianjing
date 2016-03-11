# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       urls
Date Created:   2015-08-31 14:53
Description:

"""

from django.conf.urls import url

import views.common
import views.account
import views.server
import views.character
import views.club
import views.staff
import views.item
import views.challenge
import views.building
import views.training
import views.league
import views.skill
import views.friend
import views.mail
import views.task
import views.chat
import views.notification
import views.ladder
import views.cup
import views.sponsor
import views.activity
import views.active_value
import views.shop
import views.training_match
import views.elite_match
import views.auction
import views.bag

urlpatterns = [
    url(r'^sync/$', views.common.sync),
    url(r'^ping/$', views.common.ping),

    url(r'^account/register/$', views.account.register),
    url(r'^account/login/$', views.account.login),

    url(r'^servers/$', views.server.get_server_list),
    url(r'^start/$', views.server.start_game),

    url(r'^character/create/$', views.character.create),
    url(r'^character/avatar/upload/$', views.character.save_avatar_handler),

    url(r'^club/create/$', views.club.create),
    url(r'^club/policy/$', views.club.set_policy),
    url(r'^club/matchstaff/$', views.club.set_match_staffs),
    url(r'^club/staffslots/buy/$', views.club.buy_slots),
    url(r'^club/setunit/$', views.club.set_unit),
    url(r'^club/setformation/$', views.club.set_formation),

    url(r'^staff/recruit/refresh/$', views.staff.recruit_refresh),
    url(r'^staff/recruit/$', views.staff.recruit_staff),
    url(r'^staff/fire/$', views.staff.fire),
    url(r'^staff/equipon/$', views.staff.equip_on),
    url(r'^staff/strengthen/$', views.staff.strengthen),

    url(r'^item/sell/$', views.item.sell),
    url(r'^item/use/$', views.item.use),
    url(r'^item/merge/$', views.item.merge),

    url(r'^challenge/start/$', views.challenge.start),
    url(r'^challenge/reward/$', views.challenge.reward),
    url(r'^challenge/report/$', views.challenge.report),
    url(r'^challenge/buy/$', views.challenge.buy),

    url(r'^building/levelup/$', views.building.levelup),
    url(r'^building/speedup/$', views.building.speedup),

    url(r'^training/exp/start/$', views.training.exp_start),
    url(r'^training/exp/cancel/$', views.training.exp_cancel),
    url(r'^training/exp/speedup/$', views.training.exp_speedup),
    url(r'^training/exp/getreward/$', views.training.exp_get_reward),

    url(r'^training/property/start/$', views.training.property_start),
    url(r'^training/property/cancel/$', views.training.property_cancel),
    url(r'^training/property/speedup/$', views.training.property_speedup),
    url(r'^training/property/getreward/$', views.training.property_get_reward),

    url(r'^training/broadcast/start/$', views.training.broadcast_start),
    url(r'^training/broadcast/detail/$', views.training.broadcast_detail),
    url(r'^training/broadcast/cancel/$', views.training.broadcast_cancel),
    url(r'^training/broadcast/speedup/$', views.training.broadcast_speedup),
    url(r'^training/broadcast/getreward/$', views.training.broadcast_get_reward),

    url(r'^training/shop/start/$', views.training.shop_start),
    url(r'^training/shop/sell/$', views.training.shop_sell),
    url(r'^training/shop/cancel/$', views.training.shop_cancel),

    url(r'^training/sponsor/start/$', views.training.sponsor_start),

    #
    url(r'^league/challenge/$', views.league.challenge),
    url(r'^league/report/$', views.league.report),
    url(r'^league/refresh/$', views.league.refresh),
    url(r'^league/reward/$', views.league.get_reward),
    url(r'^league/detail/$', views.league.get_detail),

    url(r'^skill/locktoggle/$', views.skill.lock_toggle),
    url(r'^skill/wash/$', views.skill.wash),
    url(r'^skill/upgrade/$', views.skill.upgrade),
    url(r'^skill/upgrade/speedup/$', views.skill.upgrade_speedup),

    url(r'^friend/info/$', views.friend.get_info),
    url(r'^friend/add/$', views.friend.add),
    url(r'^friend/remove/$', views.friend.remove),
    url(r'^friend/accept/$', views.friend.accept),
    url(r'^friend/match/$', views.friend.match),
    url(r'^friend/candidates/$', views.friend.get_candidates),

    url(r'^mail/send/$', views.mail.send),
    url(r'^mail/open/$', views.mail.read),
    url(r'^mail/delete/$', views.mail.delete),
    url(r'^mail/getattachment/$', views.mail.get_attachment),

    url(r'^task/getreward/$', views.task.reward),
    url(r'^task/doing/$', views.task.doing),

    url(r'^randomevent/done/$', views.task.random_event_done),

    url(r'^chat/send/$', views.chat.send),

    url(r'^notification/open/$', views.notification.open),
    url(r'^notification/delete/$', views.notification.delete),

    # url(r'^ladder/refresh/$', views.ladder.refresh),
    url(r'^ladder/match/$', views.ladder.match),
    url(r'^ladder/leaderboard/$', views.ladder.get_leader_board),
    url(r'^ladder/store/buy/$', views.ladder.store_buy),
    url(r'^ladder/store/refresh/$', views.ladder.store_refresh),
    url(r'^ladder/store/report/$', views.ladder.match_report),
    url(r'^ladder/buy/$', views.ladder.buy_times),

    url(r'^cup/join/$', views.cup.join),
    url(r'^cup/infomation/$', views.cup.information),

    url(r'^sponsor/$', views.sponsor.sponsor),
    url(r'^sponsor/getincome/$', views.sponsor.get_income),

    url(r'^signin/$', views.activity.signin),
    url(r'^activity/loginreward/$', views.activity.get_login_reward),

    url(r'^activevalue/getreward/$', views.active_value.get_reward),

    url(r'^itemshop/buy/$', views.shop.item_shop_buy),

    url(r'^trainingmatch/start/$', views.training_match.start),
    url(r'^trainingmatch/report/$', views.training_match.match_report),
    url(r'^trainingmatch/detail/$', views.training_match.match_detail),
    url(r'^trainingmatch/store/buy/$', views.training_match.store_buy),
    url(r'^trainingmatch/store/refresh/$', views.training_match.store_refresh),

    url(r'^elite/start/$', views.elite_match.start),
    url(r'^elite/reward/$', views.elite_match.reward),
    url(r'^elite/report/$', views.elite_match.report),

    url(r'^auction/search/$', views.auction.search),
    url(r'^auction/sell/$', views.auction.sell),
    url(r'^auction/cancel/$', views.auction.cancel),
    url(r'^auction/bidding/$', views.auction.bidding),

    url(r'^bagitem/use/$', views.bag.item_use),
    url(r'^bagitem/merge/$', views.bag.item_merge),
    url(r'^bagitem/destroy/$', views.bag.item_destroy),
    url(r'^bagequipment/destroy/$', views.bag.equipment_destroy),
    url(r'^bagequipment/levelup/$', views.bag.equipment_level_up),
    url(r'^bagequipment/levelup/confirm/$', views.bag.equipment_level_up_confirm),
]
