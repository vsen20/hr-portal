from django.contrib import admin

from .models import Department, Position, Employee, EmployeeDocument


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "name", "parent")
    list_filter = ("organization",)
    search_fields = ("name",)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "name")
    list_filter = ("organization",)
    search_fields = ("name",)


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization",
        "last_name",
        "first_name",
        "employment_status",
        "employment_type",
        "department",
        "position",
        "manager",
    )
    list_filter = ("organization", "employment_status", "employment_type", "department", "position")
    search_fields = ("first_name", "last_name")

    inlines = [EmployeeDocumentInline]
