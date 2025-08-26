from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_structure, name='structure'),
    path('employee/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('department/<int:pk>/', views.department_detail, name='department_detail'),
]