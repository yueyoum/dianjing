# -*- coding: utf-8 -*-

import os

from django.http import JsonResponse
from django.shortcuts import render_to_response
from apps.config.models import Config, CustomerServiceInformation, Bulletin


def get_config(request):
    c = Config.get_config()
    data = {
        'version': c.version,
        'url': "http://{0}/upload/{1}".format(request.get_host(), os.path.basename(c.client_config.path))
    }
    # NOTE: 如果是 负载均衡 部署到其他机器，如果目录结构不一样 这里 c.client_config.path 就要报错
    # 解决办法就是 nginx 负载规则把 /system/ 的请求都发送到 Master 服务器

    for cs in CustomerServiceInformation.objects.all():
        data[cs.name] = cs.value

    return JsonResponse(data)


def get_bulletins(request):
    width = request.GET.get('width', '')
    if width:
        width = width + "px"
    else:
        width = "device-width"

    bulletins = []
    for b in Bulletin.objects.filter(display=True).order_by('-order_num'):
        if b.image:
            image_url = "http://{0}/upload/{1}".format(request.get_host(), os.path.basename(b.image.path))
        else:
            image_url = ""

        data = {
            'title': b.title,
            'content': b.content.replace("\r\n", "<br/>"),
            'image': image_url
        }

        bulletins.append(data)

    context = {
        'width': width,
        'bulletins': bulletins
    }

    return render_to_response("bulletin.html", context)
