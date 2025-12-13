from django.contrib import admin
from .models import Organization, OrgSettings, OrgModule


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')


@admin.register(OrgSettings)
class OrgSettingsAdmin(admin.ModelAdmin):
    list_display = ('organization', 'timezone', 'language', 'currency')


@admin.register(OrgModule)
class OrgModuleAdmin(admin.ModelAdmin):
    list_display = ('organization', 'code', 'enabled')
    list_filter = ('code', 'enabled')
