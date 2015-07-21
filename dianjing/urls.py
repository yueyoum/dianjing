from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    # Examples:
    # url(r'^$', 'dianjing.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

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

    url(r'^game/challenge/start/$', 'views.challenge.start'),

    url(r'^game/building/levelup/$', 'views.building.levelup'),

    url(r'^game/training/buy/$', 'views.training.buy'),

    url(r'^game/staff/training/$', 'views.training.training'),

    url(r'^game/staff/training/getreward/$', 'views.staff.training_get_reward'),
    #
    # url(r'^game/league/statistics/$', apps.league.views.get_statistics),
    # url(r'^game/league/log/$', apps.league.views.get_battle_log),
]
