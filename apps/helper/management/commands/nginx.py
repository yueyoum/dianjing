# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       nginx.py
Date Created:   2015-12-24 10:34
Description:

"""

import sys

from django.core.management.base import BaseCommand
from django.conf import settings

str_example = """upstream uwsgi_dianjing {
    server 127.0.0.1:8001;
}

server {
    listen 8000 default_server;
    access_log  off;
    error_log   off;

    location /static/ {
        alias %s/static/;
    }

    location /upload/ {
        alias %s/upload/;
    }

    location / {
        uwsgi_pass uwsgi_dianjing;
        include uwsgi_params;
    }
}
"""

class Command(BaseCommand):
    def handle(self, *args, **options):
        sys.stdout.write(str_example % (settings.BASE_DIR, settings.UPLOAD_DIR))
