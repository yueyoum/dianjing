from django.contrib import admin

from apps.staff.models import Staff, StaffTraining

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'club_id', 'in_battle', 'oid', 'level', 'exp', 'status', 'create_at',
        'property_add', 'skills', 'winning_rate'
    )

@admin.register(StaffTraining)
class StaffTrainingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'staff_id', 'training_id', 'start_at'
    )
