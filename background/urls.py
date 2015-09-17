# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       urls
Date Created:   2015-08-31 14:45
Description:

"""

from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'background.views.data'),
    url(r'^server/$', 'background.views.servers'),
    url(r'^search/$', 'background.views.search'),
    url(r'^mail/$', 'background.views.mails'),
    url(r'^mail/one/$', 'background.views.mail_one'),
    url(r'^staff/$', 'background.views.staff'),
    url(r'^knapsack/$', 'background.views.knapsack'),
    url(r'^friend/$', 'background.views.friend'),
]
