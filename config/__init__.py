# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       __init__
Date Created:   2015-04-23 23:09
Description:

"""

import os
import json
import zipfile
from django.conf import settings


CONFIG = None


class _Config(object):
    pass


def _load_config():
    global CONFIG
    if CONFIG is not None:
        return


    attr_dict = {}

    z = zipfile.ZipFile(os.path.join(settings.BASE_DIR, 'config', settings.CONFIG_ZIP_FILE))
    for item in z.namelist():

        name, ext = os.path.splitext(item)
        content = z.open(item).read()
        if not content:
            continue

        data = json.loads(z.open(item).read())

        attr_name = name.upper()
        attr_value = {}

        if attr_name == 'ERRORMSG':
            for d in data:
                obj = _Config()
                obj.id = d['pk']
                for k, v in d['fields'].iteritems():
                    setattr(obj, k, v)

                attr_value[d['fields']['error_index']] = obj
        else:
            for d in data:
                obj = _Config()
                obj.id = d['pk']
                for k, v in d['fields'].iteritems():
                    setattr(obj, k, v)

                attr_value[obj.id] = obj

        attr_dict[attr_name] = attr_value


    CONFIG = type('CONFIG', (object,), attr_dict)

    print "LOAD CONFIG DONE. {0}".format(settings.CONFIG_ZIP_FILE)


