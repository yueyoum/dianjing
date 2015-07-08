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

    # url(r'^game/staff/training/$', apps.staff.views.training_start),
    # url(r'^game/staff/training/getreward/$', apps.staff.views.training_get_reward),
    #
    # url(r'^game/league/statistics/$', apps.league.views.get_statistics),
    # url(r'^game/league/log/$', apps.league.views.get_battle_log),
]
