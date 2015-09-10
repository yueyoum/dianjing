import os

from django.shortcuts import render_to_response
from apps.system.models import Bulletin



def get_bulletins(request):
    width = request.GET.get('width', '')
    if width:
        width = width+"px"
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
