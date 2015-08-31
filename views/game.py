# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2015-08-31 18:59
Description:

"""

from django.conf import settings
from django.http import HttpResponse

def get_version(request):
    return HttpResponse(settings.GAME_VERSION, content_type='text/plain')
