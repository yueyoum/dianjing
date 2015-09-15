from django.contrib import admin

from apps.config.models import Config, CustomerServiceInformation

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('version', 'config', 'des', 'in_use')


@admin.register(CustomerServiceInformation)
class CustomerServiceInformationAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'des')
