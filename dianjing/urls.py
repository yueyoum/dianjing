from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    # Examples:
    # url(r'^$', 'dianjing.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^game/sync/$', 'views.sync.sync'),

    url(r'^game/account/register/$', 'views.account.register'),
    url(r'^game/account/login/$', 'views.account.login'),

    url(r'^game/servers/$', 'views.server.get_server_list'),
    url(r'^game/start/$', 'views.server.start_game'),

    url(r'^game/character/create/$', 'views.character.create'),

    url(r'^game/club/create/$', 'views.club.create'),
    url(r'^game/club/policy/$', 'views.club.set_policy'),
    url(r'^game/club/matchstaff/$', 'views.club.set_match_staffs'),

    url(r'^game/staff/recruit/refresh/$', 'views.staff.recruit_refresh'),
    url(r'^game/staff/recruit/$', 'views.staff.recruit_staff'),
    url(r'^game/staff/fire/$', 'views.staff.fire'),

    url(r'^game/challenge/start/$', 'views.challenge.start'),

    url(r'^game/building/levelup/$', 'views.building.levelup'),

    url(r'^game/training/buy/$', 'views.training.buy'),

    url(r'^game/staff/training/$', 'views.training.training'),

    url(r'^game/staff/training/getreward/$', 'views.staff.training_get_reward'),
    #
    url(r'^game/league/statistics/$', 'views.league.get_statistics'),
    url(r'^game/league/log/$', 'views.league.get_log'),

    url(r'^game/skill/locktoggle/$', 'views.skill.lock_toggle'),
    url(r'^game/skill/wash/$', 'views.skill.wash'),

    url(r'^game/friend/info/$', 'views.friend.get_info'),
    url(r'^game/friend/add/$', 'views.friend.add'),
    url(r'^game/friend/remove/$', 'views.friend.remove'),
    url(r'^game/friend/accept/$', 'views.friend.accept'),
    url(r'^game/friend/match/$', 'views.friend.match'),

    url(r'^game/mail/send/$', 'views.mail.send'),
    url(r'^game/mail/open/$', 'views.mail.read'),
    url(r'^game/mail/delete/$', 'views.mail.delete'),
    url(r'^game/mail/getattachment/$', 'views.mail.get_attachment'),

    url(r'^game/task/acquire/$', 'views.task.receive'),
    url(r'^game/task/getreward/$', 'views.task.reward'),

    url(r'^game/chat/send/$', 'views.chat.send'),

    url(r'game/notification/open/$', 'views.notification.open'),
]

