from django.contrib import admin

from apps.system.models import Bulletin

@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'image', 'order_num', 'display')
    ordering = ['-order_num',]
    list_filter = ['display',]
