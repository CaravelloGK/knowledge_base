from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Department, Employee


def staff_structure(request):
    search_query = request.GET.get('search', '')

    top_level_departments = Department.objects.filter(
        parent_department__isnull=True
    )

    employees = Employee.objects.all()
    if search_query:
        employees = employees.filter(
            Q(full_name__icontains=search_query) |
            Q(position__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

    context = {
        'departments': top_level_departments,
        'search_query': search_query,
        'employees': employees,
    }
    return render(request, 'staff/structure.html', context)


def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    subordinates = employee.get_subordinates()  # Используем метод

    context = {
        'employee': employee,
        'subordinates': subordinates,
    }
    return render(request, 'staff/employee_detail.html', context)


def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    employees = department.get_employees()  # Используем метод
    child_departments = department.get_children()  # Используем метод

    context = {
        'department': department,
        'employees': employees,
        'child_departments': child_departments,
    }
    return render(request, 'staff/department_detail.html', context)