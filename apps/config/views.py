import os

from django.http import JsonResponse
from apps.config.models import Config


def get_config(request):
    c = Config.get_config()
    data = {
        'version': c.version,
        'url': "http://{0}/upload/{1}".format(request.get_host(), os.path.basename(c.config.path))
    }

    return JsonResponse(data)
