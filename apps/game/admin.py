from django.contrib import admin

from duckadmin import DuckAdmin

from apps.game.forms import FormOperationLog

@admin.register(FormOperationLog)
class AdminOperationLog(DuckAdmin):
    duck_form = FormOperationLog
