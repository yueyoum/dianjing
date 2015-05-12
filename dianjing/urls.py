from django.conf.urls import include, url
from django.contrib import admin

import apps.account.views
import apps.server.views
import apps.character.views
import apps.club.views
import apps.staff.views

urlpatterns = [
    # Examples:
    # url(r'^$', 'dianjing.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^game/account/register/$', apps.account.views.register),
    url(r'^game/account/login/$', apps.account.views.login),

    url(r'^game/servers/$', apps.server.views.get_server_list),
    url(r'^game/start/$', apps.server.views.start_game),

    url(r'^game/character/create/$', apps.character.views.create),

    url(r'^game/club/create/$', apps.club.views.create),

    url(r'^game/staff/training/$', apps.staff.views.training_start),
    url(r'^game/staff/training/getreward/$', apps.staff.views.training_get_reward),
]
