# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.contrib.admin.helpers import ActionForm
from django.contrib import messages

from apps.character.models import Character

from core.mongo import MongoCharacter


class MyActionForm(ActionForm):
    value = forms.IntegerField(required=True)


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'account_id', 'server_id', 'name', 'create_at',
        'club_name',
        'Info'
    )

    search_fields = ['name', ]

    action_form = MyActionForm
    actions = ['add_gold', 'add_diamond', 'add_club_level']

    def Info(self, obj):
        doc = MongoCharacter.db(obj.server_id).find_one(
            {'_id': obj.id},
            {
                'club.gold': 1,
                'club.diamond': 1,
                'club.level': 1
            }
        )

        if not doc:
            gold = diamond = level = 'None'
        else:
            gold = doc.get('club', {}).get('gold', 'None')
            diamond = doc.get('club', {}).get('diamond', 'None')
            level = doc.get('club', {}).get('level', 'None')

        return "软妹币  : {0}<br/>钻石   : {1}<br/>俱乐部等级: {2}".format(
            gold, diamond, level
        )

    Info.allow_tags = True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def modify_club(self, request, queryset, name):
        try:
            value = int(request.POST['value'])
        except:
            self.message_user(request, "填入的数字错误", level=messages.ERROR)
            return False

        key = "club.{0}".format(name)
        for q in queryset:
            doc = MongoCharacter.db(q.server_id).find_one({'_id': q.id}, {'club': 1})
            if not doc or 'club' not in doc:
                continue

            MongoCharacter.db(q.server_id).update_one(
                {'_id': q.id},
                {'$set': {key: value}}
            )

        self.message_user(request, "设置成功")

    def add_gold(self, request, queryset):
        self.modify_club(request, queryset, 'gold')

    add_gold.short_description = "设置软妹币"

    def add_diamond(self, request, queryset):
        self.modify_club(request, queryset, 'diamond')

    add_diamond.short_description = "设置钻石"

    def add_club_level(self, request, queryset):
        self.modify_club(request, queryset, 'level')

    add_club_level.short_description = "设置俱乐部等级"
