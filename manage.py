#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    import pymysql
    pymysql.install_as_MySQLdb()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dianjing.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
