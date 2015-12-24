# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       nginx.py
Date Created:   2015-12-24 10:34
Description:

"""

import sys

from django.core.management.base import BaseCommand
from dianjing.settings import BASE_DIR

str_example = """
upstream uwsgi_dianjing {
    server 127.0.0.1:8001;
}

server {
    listen 8000 default_server;
    access_log  off;
    error_log   off;

    location /static/ {
        alias %s;
    }

    location /upload/ {
        alias %s;
    }

    location / {
        uwsgi_pass uwsgi_dianjing;
        include uwsgi_params;
    }
}
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        output_file = sys.stdout
        output_file.write(str_example % (str(BASE_DIR) + r'/static/', str(BASE_DIR) + r'/upload/'))
        print output_file
