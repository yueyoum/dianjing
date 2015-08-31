# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       urls
Date Created:   2015-08-31 14:53
Description:

"""

from django.conf.urls import url

urlpatterns = [
    url(r'^sync/$', 'views.sync.sync'),

    url(r'^account/register/$', 'views.account.register'),
    url(r'^account/login/$', 'views.account.login'),

    url(r'^servers/$', 'views.server.get_server_list'),
    url(r'^start/$', 'views.server.start_game'),

    url(r'^character/create/$', 'views.character.create'),

    url(r'^club/create/$', 'views.club.create'),
    url(r'^club/policy/$', 'views.club.set_policy'),
    url(r'^club/matchstaff/$', 'views.club.set_match_staffs'),

    url(r'^staff/recruit/refresh/$', 'views.staff.recruit_refresh'),
    url(r'^staff/recruit/$', 'views.staff.recruit_staff'),
    url(r'^staff/fire/$', 'views.staff.fire'),

    url(r'^challenge/start/$', 'views.challenge.start'),

    url(r'^building/levelup/$', 'views.building.levelup'),

    url(r'^training/buy/$', 'views.training.buy'),
    url(r'^training/refresh/$', 'views.training.refresh'),

    url(r'^staff/training/$', 'views.training.training'),

    url(r'^staff/training/getreward/$', 'views.staff.training_get_reward'),
    #
    url(r'^league/statistics/$', 'views.league.get_statistics'),
    url(r'^league/log/$', 'views.league.get_log'),

    url(r'^skill/locktoggle/$', 'views.skill.lock_toggle'),
    url(r'^skill/wash/$', 'views.skill.wash'),

    url(r'^friend/info/$', 'views.friend.get_info'),
    url(r'^friend/add/$', 'views.friend.add'),
    url(r'^friend/remove/$', 'views.friend.remove'),
    url(r'^friend/accept/$', 'views.friend.accept'),
    url(r'^friend/match/$', 'views.friend.match'),

    url(r'^mail/send/$', 'views.mail.send'),
    url(r'^mail/open/$', 'views.mail.read'),
    url(r'^mail/delete/$', 'views.mail.delete'),
    url(r'^mail/getattachment/$', 'views.mail.get_attachment'),

    url(r'^task/acquire/$', 'views.task.receive'),
    url(r'^task/getreward/$', 'views.task.reward'),

    url(r'^chat/send/$', 'views.chat.send'),

    url(r'^notification/open/$', 'views.notification.open'),

    url(r'^ladder/refresh/$', 'views.ladder.refresh'),
    url(r'^ladder/match/$', 'views.ladder.match'),

    url(r'^cup/join/$', 'views.cup.join'),
    url(r'^cup/infomation/$', 'views.cup.information'),
]
