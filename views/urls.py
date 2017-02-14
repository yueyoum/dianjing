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
import views.club
import views.staff
import views.challenge
import views.friend
import views.mail
import views.task
import views.chat
import views.notification
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
import views.welfare
import views.union
import views.purchase
import views.activity
import views.plunder
import views.inspire
import views.championship
import views.leaderboard
import views.misc

urlpatterns = [
    url(r'^sync/$', views.common.sync),
    url(r'^ping/$', views.common.ping),

    url(r'^account/register/$', views.account.register),
    url(r'^account/login/$', views.account.login),

    url(r'^servers/$', views.server.get_server_list),
    url(r'^start/$', views.server.start_game),

    url(r'^club/create/$', views.club.create),
    url(r'^club/leaderboard/$', views.club.get_leaderboard),

    url(r'^formation/setstaff/$', views.formation.set_staff),
    url(r'^formation/setunit/$', views.formation.set_unit),
    url(r'^formation/active/$', views.formation.active),
    url(r'^formation/levelup/$', views.formation.level_up),
    url(r'^formation/use/$', views.formation.use),

    url(r'^staff/recruit/$', views.staff.recruit),

    url(r'^staff/equipchange/$', views.staff.equipment_change),
    url(r'^staff/levelup/$', views.staff.level_up),
    url(r'^staff/stepup/$', views.staff.step_up),
    url(r'^staff/starup/$', views.staff.star_up),
    url(r'^staff/destroy/$', views.staff.destroy),
    url(r'^staff/batchdestroy/$', views.staff.batch_destroy),

    url(r'^challenge/start/$', views.challenge.start),
    url(r'^challenge/sweep/$', views.challenge.sweep),
    url(r'^challenge/reset/$', views.challenge.reset),
    url(r'^challenge/chapter/reward/$', views.challenge.chapter_reward),
    url(r'^challenge/report/$', views.challenge.report),

    url(r'^friend/info/$', views.friend.get_info),
    url(r'^friend/add/$', views.friend.add),
    url(r'^friend/remove/$', views.friend.remove),
    url(r'^friend/accept/$', views.friend.accept),
    url(r'^friend/candidates/$', views.friend.get_candidates),

    url(r'^mail/send/$', views.mail.send),
    url(r'^mail/open/$', views.mail.read),
    url(r'^mail/delete/$', views.mail.delete),
    url(r'^mail/getattachment/$', views.mail.get_attachment),

    url(r'^taskdaily/getreward/$', views.task.task_daily_get_reward),

    url(r'^chat/send/$', views.chat.send),

    url(r'^notification/open/$', views.notification.open),
    url(r'^notification/delete/$', views.notification.delete),

    url(r'^bagitem/use/$', views.bag.item_use),
    url(r'^bagitem/merge/$', views.bag.item_merge),
    url(r'^bagitem/destroy/$', views.bag.item_destroy),
    url(r'^bagequipment/destroy/$', views.bag.equipment_destroy),
    url(r'^bagequipment/batchdestroy/$', views.bag.equipment_batch_destroy),
    url(r'^bagequipment/levelup/$', views.bag.equipment_level_up),

    url(r'^unit/levelup/$', views.unit.level_up),
    url(r'^unit/stepup/$', views.unit.step_up),
    url(r'^unit/destroy/$', views.unit.destroy),

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
    url(r'^territory/friend/match/$', views.territory.friend_match_start),
    url(r'^territory/friend/report/$', views.territory.friend_report),
    url(r'^territory/inspire/$', views.territory.inspire),

    url(r'^store/buy/$', views.store.buy),
    url(r'^store/refresh/$', views.store.refresh),
    url(r'^store/autorefresh/$', views.store.auto_refresh),

    url(r'^vip/buyreward/$', views.vip.buy_reward),

    url(r'^energy/buy/$', views.energy.buy),

    url(r'^welfare/signin/$', views.welfare.signin),
    url(r'^welfare/newplayer/$', views.welfare.new_player_get),
    url(r'^welfare/levelreward/$', views.welfare.level_reward_get),
    url(r'^welfare/energyreward/$', views.welfare.energy_reward_get),

    url(r'^union/create/$', views.union.create),
    url(r'^union/setbulletin/$', views.union.set_bulletin),
    url(r'^union/list/$', views.union.get_list),
    url(r'^union/apply/$', views.union.apply_union),
    url(r'^union/agree/$', views.union.agree),
    url(r'^union/refuse/$', views.union.refuse),
    url(r'^union/kick/$', views.union.kick),
    url(r'^union/transfer/$', views.union.transfer),
    url(r'^union/quit/$', views.union.quit),
    url(r'^union/signin/$', views.union.signin),
    url(r'^union/explore/leaderboard/$', views.union.explore_leader_board),
    url(r'^union/explore/$', views.union.explore),
    url(r'^union/harass/query/$', views.union.harass_query_union),
    url(r'^union/harass/$', views.union.harass),
    url(r'^union/harass/buytimes/$', views.union.harass_buy_times),
    url(r'^union/skill/levelup/$', views.union.skill_level_up),

    url(r'^purchase/verify/$', views.purchase.verify),
    url(r'^purchase/getfirstreward/$', views.purchase.get_first_reward),

    url(r'^activity/newplayer/getreward/$', views.activity.newplayer_getreward),
    url(r'^activity/newplayer/dailybuy/$', views.activity.newplayer_dailybuy),

    url(r'^plunder/formation/setstaff/$', views.plunder.set_staff),
    url(r'^plunder/formation/setunit/$', views.plunder.set_unit),
    url(r'^plunder/search/$', views.plunder.search),
    url(r'^plunder/spy/$', views.plunder.spy),
    url(r'^plunder/start/$', views.plunder.start),
    url(r'^plunder/report/$', views.plunder.report),
    url(r'^plunder/getreward/$', views.plunder.get_reward),
    url(r'^plunder/buytimes/$', views.plunder.buy_plunder_times),
    url(r'^plunder/dailyreward/get/$', views.plunder.get_daily_reward),
    url(r'^plunder/station/sync/$', views.plunder.sync_station),
    url(r'^plunder/station/getproduct/$', views.plunder.get_station_product),

    url(r'^plunder/specialequip/generate/$', views.plunder.special_equipment_generate),
    url(r'^plunder/specialequip/speedup/$', views.plunder.special_equipment_speedup),
    url(r'^plunder/specialequip/get/$', views.plunder.special_equipment_get),

    url(r'^inspire/setstaff/$', views.inspire.set_staff),

    url(r'^champion/formation/setstaff/$', views.championship.set_staff),
    url(r'^champion/formation/setunit/$', views.championship.set_unit),
    url(r'^champion/formation/setposition/$', views.championship.set_position),
    url(r'^champion/apply/$', views.championship.apply_in),
    url(r'^champion/bet/$', views.championship.bet),
    url(r'^champion/group/sync/$', views.championship.sync_group),
    url(r'^champion/level/sync/$', views.championship.sync_level),

    url(r'^leaderboard/worship/$', views.leaderboard.worship),
    url(r'^leaderboard/arena/chat/$', views.leaderboard.arena_chat),
    url(r'^leaderboard/arena/approval/$', views.leaderboard.arena_approval),
    url(r'^leaderboard/plunder/chat/$', views.leaderboard.plunder_chat),
    url(r'^leaderboard/plunder/approval/$', views.leaderboard.plunder_approval),
    url(r'^leaderboard/championship/chat/$', views.leaderboard.championship_chat),
    url(r'^leaderboard/championship/approval/$', views.leaderboard.championship_approval),

    url(r'^match/log/$', views.misc.get_match_log),
]
