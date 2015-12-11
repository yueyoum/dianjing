# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       urls
Date Created:   2015-08-31 14:53
Description:

"""

from django.conf.urls import url

import views.api.timerd

urlpatterns = [
    url(r'^timerd/building/$', views.api.timerd.building_levelup_callback),
    url(r'^timerd/training/exp/$', views.api.timerd.training_exp_callback),
    url(r'^timerd/training/property/$', views.api.timerd.training_property_callback),
    url(r'^timerd/training/broadcast/$', views.api.timerd.training_broadcast_callback),
    url(r'^timerd/skill/$', views.api.timerd.skill_upgrade_callback),
]
