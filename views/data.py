# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       data
Date Created:   2015-08-03 13:45
Description:

"""

from django.http import HttpResponse

def data(request):
    return HttpResponse('hello word')

