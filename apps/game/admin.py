from django.contrib import admin

from duckadmin import DuckAdmin

from apps.game.forms import MyForm

@admin.register(MyForm)
class MyAdmin(DuckAdmin):
    duck_form = MyForm
