from django.conf.urls import include, url
from django.contrib import admin

import apps.account.views

urlpatterns = [
    # Examples:
    # url(r'^$', 'dianjing.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^/game/account/register/$', apps.account.views.register),
    url(r'^/game/account/login/$', apps.account.views.login),
]
