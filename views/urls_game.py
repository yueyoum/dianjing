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
import views.challenge
import views.friend
import views.mail
import views.task
import views.chat
import views.notification
import views.sponsor
import views.activity
import views.active_value
import views.shop
import views.auction
import views.bag
import views.unit
import views.formation
import views.talent
import views.dungeon
import views.arena
import views.tower
import views.territory
import views.store
import views.vip
import views.energy

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

    url(r'^formation/setstaff/$', views.formation.set_staff),
    url(r'^formation/setunit/$', views.formation.set_unit),
    url(r'^formation/moveslot/$', views.formation.move_slot),

    url(r'^staff/recruit/$', views.staff.recruit),

    url(r'^staff/equipchange/$', views.staff.equipment_change),
    url(r'^staff/levelup/$', views.staff.level_up),
    url(r'^staff/stepup/$', views.staff.step_up),
    url(r'^staff/starup/$', views.staff.star_up),
    url(r'^staff/destroy/$', views.staff.destroy),

    url(r'^challenge/start/$', views.challenge.start),
    url(r'^challenge/sweep/$', views.challenge.sweep),
    url(r'^challenge/reset/$', views.challenge.reset),
    url(r'^challenge/chapter/reward/$', views.challenge.chapter_reward),
    url(r'^challenge/report/$', views.challenge.report),

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

    url(r'^randomevent/done/$', views.task.random_event_done),
    url(r'^taskdaily/getreward/$', views.task.task_daily_get_reward),

    url(r'^chat/send/$', views.chat.send),

    url(r'^notification/open/$', views.notification.open),
    url(r'^notification/delete/$', views.notification.delete),

    url(r'^sponsor/$', views.sponsor.sponsor),
    url(r'^sponsor/getincome/$', views.sponsor.get_income),

    url(r'^signin/$', views.activity.signin),
    url(r'^activity/loginreward/$', views.activity.get_login_reward),

    url(r'^activevalue/getreward/$', views.active_value.get_reward),

    url(r'^itemshop/buy/$', views.shop.item_shop_buy),

    url(r'^auction/search/$', views.auction.search),
    url(r'^auction/sell/$', views.auction.sell),
    url(r'^auction/cancel/$', views.auction.cancel),
    url(r'^auction/bidding/$', views.auction.bidding),

    url(r'^bagitem/use/$', views.bag.item_use),
    url(r'^bagitem/merge/$', views.bag.item_merge),
    url(r'^bagitem/destroy/$', views.bag.item_destroy),
    url(r'^bagequipment/destroy/$', views.bag.equipment_destroy),
    url(r'^bagequipment/levelup/$', views.bag.equipment_level_up_preview),
    url(r'^bagequipment/levelup/confirm/$', views.bag.equipment_level_up_confirm),

    url(r'^unit/levelup/$', views.unit.level_up),
    url(r'^unit/stepup/$', views.unit.step_up),

    url(r'^talent/levelup/$', views.talent.level_up),
    url(r'^talent/reset/$', views.talent.reset),

    url(r'^dungeon/start/$', views.dungeon.start),
    url(r'^dungeon/report/$', views.dungeon.report),
    url(r'^dungeon/buytimes/$', views.dungeon.buy_times),

    url(r'^arena/refresh/$', views.arena.refresh),
    url(r'^arena/leaderboard/$', views.arena.leader_board),
    url(r'^arena/matchstart/$', views.arena.match_start),
    url(r'^arena/matchreport/$', views.arena.match_report),
    url(r'^arena/honorreward/$', views.arena.get_honor_reward),
    url(r'^arena/buytimes/$', views.arena.buy_times),

    url(r'^tower/matchstart/$', views.tower.match_start),
    url(r'^tower/matchreport/$', views.tower.match_report),
    url(r'^tower/reset/$', views.tower.reset),
    url(r'^tower/sweep/$', views.tower.sweep),
    url(r'^tower/sweepfinish/$', views.tower.sweep_finish),
    url(r'^tower/turntable/$', views.tower.turntable_pick),
    url(r'^tower/leaderboard/$', views.tower.get_leader_board),
    url(r'^tower/goodsbuy/$', views.tower.buy_goods),

    url(r'^territory/start/$', views.territory.start),
    url(r'^territory/getreward/$', views.territory.get_reward),
    url(r'^territory/store/buy/$', views.territory.store_buy),
    url(r'^territory/friend/list/$', views.territory.friend_list),
    url(r'^territory/friend/help/$', views.territory.friend_help),
    url(r'^territory/friend/report/$', views.territory.friend_report),
    url(r'^territory/inspire/$', views.territory.inspire),

    url(r'^store/buy/$', views.store.buy),
    url(r'^store/refresh/$', views.store.refresh),
    url(r'^store/autorefresh/$', views.store.auto_refresh),

    url(r'^vip/buyreward/$', views.vip.buy_reward),

    url(r'^energy/buy/$', views.energy.buy),
]
