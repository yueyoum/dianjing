import os

from django.http import JsonResponse
from apps.config.models import Config, CustomerServiceInformation


def get_config(request):
    c = Config.get_config()
    data = {
        'version': c.version,
        'url': "http://{0}/upload/{1}".format(request.get_host(), os.path.basename(c.config.path))
    }

    for cs in CustomerServiceInformation.objects.all():
        data[cs.name] = cs.value

    return JsonResponse(data)
