# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.contrib.admin.helpers import ActionForm
from django.contrib import messages

from apps.character.models import Character

from core.mongo import MongoCharacter
from core.package import Drop
from core.resource import Resource
from core.signals import purchase_done_signal


class MyActionForm(ActionForm):
    value = forms.CharField(required=True)


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'account_id', 'server_id', 'name', 'create_at',
        'club_name', 'last_login', 'login_times',
        'Info'
    )

    list_per_page = 50

    search_fields = ['name', 'club_name', ]

    action_form = MyActionForm
    actions = ['add_gold', 'add_diamond', 'add_club_level', 'add_ladder_score', 'add_purchase_diamond',
               'add_training_skill_item', 'add_item',
               ]

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


    def check_value(self, request):
        try:
            return int(request.POST['value'])
        except:
            self.message_user(request, u"填入的数字错误", level=messages.ERROR)
            return False

    def check_value_and_amount(self, request):
        try:
            data = request.POST['value']
            value, amount = data.split(':')
            return int(value), int(amount)
        except:
            self.message_user(request, u"应该填入ID:数量", level=messages.ERROR)
            return False, False


    def add_gold(self, request, queryset):
        value = self.check_value(request)
        if not value:
            return

        drop = Drop()
        drop.gold = value

        for q in queryset:
            Resource(q.server_id, q.id).save_drop(drop, message=u"From Admin")

    add_gold.short_description = u"添加软妹币"

    def add_diamond(self, request, queryset):
        value = self.check_value(request)
        if not value:
            return

        drop = Drop()
        drop.diamond = value

        for q in queryset:
            Resource(q.server_id, q.id).save_drop(drop, message=u"From Admin")

    add_diamond.short_description = u"添加钻石"

    def add_club_level(self, request, queryset):
        value = self.check_value(request)
        if not value:
            return

        for q in queryset:
            MongoCharacter.db(q.server_id).update_one(
                {'_id': q.id},
                {'$set': {'club.level': value}}
            )

    add_club_level.short_description = u"设置俱乐部等级"

    def add_ladder_score(self, request, queryset):
        value = self.check_value(request)
        if not value:
            return

        drop = Drop()
        drop.ladder_score = value

        for q in queryset:
            Resource(q.server_id, q.id).save_drop(drop, message=u"From Admin")

    add_ladder_score.short_description = u"添加天梯赛积分"


    def add_purchase_diamond(self, request, queryset):
        value = self.check_value(request)
        if not value:
            return

        drop = Drop()
        drop.diamond = value

        for q in queryset:
            Resource(q.server_id, q.id).save_drop(drop, message=u"From Admin. Purchase")
            purchase_done_signal.send(
                sender=None,
                server_id=q.server_id,
                char_id=q.id,
                diamond=value
            )

    add_purchase_diamond.short_description = u"添加充值钻石"


    def add_training_skill_item(self, request, queryset):
        value, amount = self.check_value_and_amount(request)
        if not value:
            return

        from config import ConfigTrainingSkillItem
        if not ConfigTrainingSkillItem.get(value):
            return

        # TODO
        from core.bag import BagTrainingSkill
        for q in queryset:
            BagTrainingSkill(q.server_id, q.id).add([(value, amount)])

    add_training_skill_item.short_description = u"添加技能训练书"

    def add_item(self, request, queryset):
        value, amount= self.check_value_and_amount(request)
        if not value:
            return

        from config import ConfigItem
        if not ConfigItem.get(value):
            return

        # TODO
        from core.bag import BagItem
        for q in queryset:
            BagItem(q.server_id, q.id).add([(value, amount)])

    add_item.short_description = u"添加道具"
