from django.contrib import admin

from .models import Department, Position, Employee, EmployeeDocument


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "name", "parent")
    list_filter = ("organization",)
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        employee = getattr(request.user, "employee_profile", None)
        if employee is None:
            return qs.none()

        return qs.filter(organization=employee.organization)



@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "name")
    list_filter = ("organization",)
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        employee = getattr(request.user, "employee_profile", None)
        if employee is None:
            return qs.none()

        return qs.filter(organization=employee.organization)

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "employee", "doc_type", "title", "issued_date", "created_at")
    list_filter = ("organization", "doc_type")
    search_fields = ("title", "identifier", "employee__first_name", "employee__last_name")

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        employee = getattr(request.user, "employee_profile", None)
        if employee is None:
            return qs.none()

        # EMPLOYEE sees only own documents (even in documents section)
        if request.user.groups.filter(name="EMPLOYEE").exists():
            return qs.filter(employee=employee)

        # ORG_ADMIN / HR_MANAGER: only org documents
        return qs.filter(organization=employee.organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_superuser:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        employee = getattr(request.user, "employee_profile", None)
        if employee is None:
            if db_field.name == "employee":
                kwargs["queryset"] = db_field.remote_field.model.objects.none()
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "employee":
            # documents can be linked only to employees from same organization
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                organization=employee.organization
            )

            # EMPLOYEE can link documents only to self (if you ever allow add)
            if request.user.groups.filter(name="EMPLOYEE").exists():
                kwargs["queryset"] = kwargs["queryset"].filter(pk=employee.pk)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization",
        "user",
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # 1) Superuser sees everything
        if request.user.is_superuser:
            return qs

        # 2) If user has no linked employee, show nothing
        employee = getattr(request.user, "employee_profile", None)
        if employee is None:
            return qs.none()

        # 3) EMPLOYEE role: only self
        if request.user.groups.filter(name="EMPLOYEE").exists():
            return qs.filter(pk=employee.pk)

        # 4) ORG_ADMIN / HR_MANAGER: only same organization
        return qs.filter(organization=employee.organization)
    
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        employee = getattr(request.user, "employee_profile", None)

        # superuser or no linked employee -> keep default behavior (or empty)
        if request.user.is_superuser:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        if employee is None:
            # no org context => prevent selecting anything
            if db_field.name in {"department", "position", "manager"}:
                kwargs["queryset"] = db_field.remote_field.model.objects.none()
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "department":
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                organization=employee.organization
            )

        if db_field.name == "position":
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                organization=employee.organization
            )

        if db_field.name == "manager":
            # manager must be an employee from the same organization
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                organization=employee.organization
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def has_view_permission(self, request, obj=None):
        # list view
        if obj is None:
            return super().has_view_permission(request, obj=obj)

        if request.user.is_superuser:
            return True

        employee = getattr(request.user, "employee_profile", None)
        if employee is None:
            return False

        # EMPLOYEE: only self
        if request.user.groups.filter(name="EMPLOYEE").exists():
            return obj.pk == employee.pk

        # ORG_ADMIN / HR_MANAGER: only same org
        return obj.organization_id == employee.organization_id

    def has_change_permission(self, request, obj=None):
        # let Django handle module-level permission first
        if not super().has_change_permission(request, obj=obj):
            return False

        if obj is None:
            return True

        if request.user.is_superuser:
            return True

        employee = getattr(request.user, "employee_profile", None)
        if employee is None:
            return False

        # EMPLOYEE: no editing other employees; usually no editing at all
        if request.user.groups.filter(name="EMPLOYEE").exists():
            return obj.pk == employee.pk and request.user.has_perm("hr_core.change_employee")

        return obj.organization_id == employee.organization_id

    def has_delete_permission(self, request, obj=None):
        if not super().has_delete_permission(request, obj=obj):
            return False

        if obj is None:
            return True

        if request.user.is_superuser:
            return True

        employee = getattr(request.user, "employee_profile", None)
        if employee is None:
            return False

        # EMPLOYEE: never delete
        if request.user.groups.filter(name="EMPLOYEE").exists():
            return False

        return obj.organization_id == employee.organization_id

