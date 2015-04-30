from django.contrib import admin

from apps.staff.models import Staff, StaffTraining

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'char_id', 'oid', 'level', 'exp', 'status', 'create_at',
        'property_add', 'skills'
    )

@admin.register(StaffTraining)
class StaffTrainingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'staff_id', 'training_id', 'start_at'
    )
