# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       admin
Date Created:   2016-07-04 15-10
Description:

"""

from django.http import HttpResponse

from utils import cache

def flushcache(request):
    cache.flush()

    return HttpResponse("Success!")