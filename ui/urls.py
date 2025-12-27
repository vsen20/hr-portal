from django.urls import path
from . import views

app_name = "ui"

urlpatterns = [
    path("", views.home, name="home"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("departments/", views.department_list, name="department_list"),
    path("positions/", views.position_list, name="position_list"),

]
