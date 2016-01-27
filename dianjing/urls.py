from django.conf.urls import include, url
from django.contrib import admin

import apps.config.views
import apps.system.views

urlpatterns = [
    # Examples:
    # url(r'^$', 'dianjing.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^game/', include('views.urls_game')),
    url(r'^api/', include('views.urls_api')),

    url(r'^system/config/$', apps.config.views.get_config),
    url(r'^system/bulletin/$', apps.system.views.get_bulletins),
]
