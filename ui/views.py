from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from hr_core.models import Employee, EmployeeDocument, Department, Position




@login_required
def home(request):
    return render(request, "ui/home.html")

@login_required
def employee_list(request):
    # Superuser: everything (dev only)
    if request.user.is_superuser:
        employees = Employee.objects.select_related(
            "organization", "department", "position", "manager", "user"
        ).all()
        return render(request, "ui/employees/list.html", {"employees": employees})

    me = getattr(request.user, "employee_profile", None)
    if me is None:
        # no employee profile -> show empty page
        return render(request, "ui/employees/list.html", {"employees": []})

    qs = Employee.objects.select_related(
        "organization", "department", "position", "manager", "user"
    ).filter(organization=me.organization)

    # EMPLOYEE: only self
    if request.user.groups.filter(name="EMPLOYEE").exists():
        qs = qs.filter(pk=me.pk)

    return render(request, "ui/employees/list.html", {"employees": qs})

@login_required
def employee_detail(request, pk: int):
    # 1) Resolve employee with scoping
    if request.user.is_superuser:
        try:
            employee = Employee.objects.select_related(
                "organization", "department", "position", "manager", "user"
            ).get(pk=pk)
        except Employee.DoesNotExist:
            raise Http404()
    else:
        me = getattr(request.user, "employee_profile", None)
        if me is None:
            raise Http404()

        qs = Employee.objects.select_related(
            "organization", "department", "position", "manager", "user"
        ).filter(organization=me.organization)

        # EMPLOYEE: only self
        if request.user.groups.filter(name="EMPLOYEE").exists():
            qs = qs.filter(pk=me.pk)

        try:
            employee = qs.get(pk=pk)
        except Employee.DoesNotExist:
            raise Http404()

    # 2) Documents: always defined
    documents = EmployeeDocument.objects.filter(employee=employee).order_by("-id")

    return render(
        request,
        "ui/employees/detail.html",
        {"employee": employee, "documents": documents},
    )

@login_required
def department_list(request):
    if request.user.is_superuser:
        departments = Department.objects.select_related("organization", "parent").all()
        return render(request, "ui/departments/list.html", {"departments": departments})

    me = getattr(request.user, "employee_profile", None)
    if me is None:
        return render(request, "ui/departments/list.html", {"departments": []})

    departments = Department.objects.select_related("organization", "parent").filter(
        organization=me.organization
    )
    return render(request, "ui/departments/list.html", {"departments": departments})

@login_required
def position_list(request):
    if request.user.is_superuser:
        positions = Position.objects.select_related("organization").all()
        return render(request, "ui/positions/list.html", {"positions": positions})

    me = getattr(request.user, "employee_profile", None)
    if me is None:
        return render(request, "ui/positions/list.html", {"positions": []})

    positions = Position.objects.select_related("organization").filter(
        organization=me.organization
    )
    return render(request, "ui/positions/list.html", {"positions": positions})
