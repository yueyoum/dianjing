import re
from collections import defaultdict

from django.contrib import admin
from django.db.models import Q
from django.contrib.admin.views.main import ChangeList

from apps.history_record.models import MailHistoryRecord


MAIL_SEARCH_PATTERN = re.compile('f(\d+)|t(\d+)')
def get_mail_search_params(text):
    p = defaultdict(lambda : [])
    for x1, x2 in MAIL_SEARCH_PATTERN.findall(text):
        if x1:
            p['f'].append(x1)
        if x2:
            p['t'].append(x2)

    return p


class MailRecordChangeList(ChangeList):
    def get_queryset(self, request):
        params = get_mail_search_params(self.query)
        if not params:
            return super(MailRecordChangeList, self).get_queryset(request)

        f = params['f']
        t = params['t']

        if len(f) > 1 or len(t) > 1:
            return super(MailRecordChangeList, self).get_queryset(request)

        condition = Q()
        if f:
            from_id = int(f[0])
            condition &= Q(from_id=from_id)
        if t:
            to_id = int(t[0])
            condition &= Q(to_id=to_id)

        return MailHistoryRecord.objects.filter(condition)


@admin.register(MailHistoryRecord)
class MailHistoryRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'from_id', 'to_id', 'title', 'content', 'has_read',
        'attachment', 'function', 'create_at',
    )

    search_fields = ['from_id', 'to_id']
    change_list_template = 'mail_record_change_list.html'

    def get_changelist(self, request, **kwargs):
        return MailRecordChangeList
