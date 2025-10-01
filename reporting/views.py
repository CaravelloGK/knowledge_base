# reports/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta

from .models import Task, Department, UserProfile
from .forms import SimpleTaskForm, QuickTaskForm


def home_redirect(request):
    """Редирект с главной страницы на логин или дашборд"""
    if request.user.is_authenticated:
        return redirect('reporting:demo_dashboard')
    else:
        return redirect('reporting:demo_login')


def demo_login(request):
    """Простая страница входа для демо"""
    if request.user.is_authenticated:
        return redirect('reporting:demo_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'reporting:demo_dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = AuthenticationForm()

    # Демо-аккаунты для показа на странице входа
    demo_accounts = [
        {'role': 'Директор', 'login': 'director', 'password': 'demo123'},
        {'role': 'Менеджер разработки', 'login': 'dev_manager', 'password': 'demo123'},
        {'role': 'Менеджер тестирования', 'login': 'qa_manager', 'password': 'demo123'},
        {'role': 'Разработчик', 'login': 'developer1', 'password': 'demo123'},
        {'role': 'Тестировщик', 'login': 'tester1', 'password': 'demo123'},
        {'role': 'Дизайнер', 'login': 'designer1', 'password': 'demo123'},
    ]

    return render(request, 'reporting/demo_login.html', {
        'form': form,
        'demo_accounts': demo_accounts
    })


def demo_logout(request):
    """Выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('reporting:demo_login')


@login_required(login_url='reporting:demo_login')
def dashboard(request):
    """Главная страница - дашборд"""
    user = request.user
    profile = user.profile

    # Завтрашняя дата для определения срочных задач
    tomorrow = timezone.now().date() + timedelta(days=1)

    # Статистика в зависимости от роли
    if profile.is_director:
        # Директор видит все
        tasks = Task.objects.all()
        departments = Department.objects.all()
        stats = []
        for dept in departments:
            dept_tasks = Task.objects.filter(assigned_to__profile__department=dept)
            stats.append({
                'department': dept,
                'total': dept_tasks.count(),
                'completed': dept_tasks.filter(status='completed').count(),
                'in_progress': dept_tasks.filter(status='in_progress').count(),
            })

        context = {
            'stats': stats,
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='completed').count(),
        }

    elif profile.is_manager and profile.department:
        # Руководитель видит свое подразделение
        tasks = Task.objects.filter(assigned_to__profile__department=profile.department)
        employees_tasks = []

        for employee in profile.department.user_set.all():
            emp_tasks = tasks.filter(assigned_to=employee)
            employees_tasks.append({
                'employee': employee,
                'total': emp_tasks.count(),
                'completed': emp_tasks.filter(status='completed').count(),
            })

        context = {
            'department': profile.department,
            'employees_tasks': employees_tasks,
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='completed').count(),
            'overdue_tasks': tasks.filter(
                planned_deadline__lt=timezone.now().date(),
                status__in=['new', 'in_progress']
            ).count(),
        }

    else:
        # Сотрудник видит только свои задачи
        tasks = Task.objects.filter(assigned_to=user)
        context = {
            'tasks': tasks.order_by('-received_date')[:5],  # Последние 5 задач
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='completed').count(),
            'urgent_tasks': tasks.filter(
                planned_deadline__lte=timezone.now().date() + timedelta(days=3),
                status__in=['new', 'in_progress']
            ).count(),
            'tomorrow': tomorrow,
        }

    context['user_profile'] = profile
    return render(request, 'reporting/demo_dashboard.html', context)


@login_required(login_url='reporting:demo_login')
def task_list(request):
    """Список задач"""
    profile = request.user.profile

    if profile.is_director:
        tasks = Task.objects.all()
    elif profile.is_manager and profile.department:
        tasks = Task.objects.filter(assigned_to__profile__department=profile.department)
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    # Простая фильтрация
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    context = {
        'tasks': tasks.order_by('-received_date'),
        'user_profile': profile,
    }
    return render(request, 'reporting/demo_task_list.html', context)


@login_required(login_url='reporting:demo_login')
def create_task(request):
    """Создание задачи"""
    if request.method == 'POST':
        form = SimpleTaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_to = request.user  # По умолчанию назначаем на себя
            task.save()
            messages.success(request, 'Задача успешно создана!')
            return redirect('reporting:demo_dashboard')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = SimpleTaskForm(user=request.user, initial={
            'received_date': timezone.now().date(),
            'planned_deadline': timezone.now().date() + timedelta(days=7)
        })

    return render(request, 'reporting/demo_task_form.html', {'form': form})


@login_required(login_url='demo_login')
def quick_create_task(request):
    """Быстрое создание задачи (AJAX)"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = QuickTaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_to = request.user
            task.received_date = timezone.now().date()
            task.customer = "Внутренний"
            task.status = 'new'
            task.save()
            return JsonResponse({'success': True, 'task_id': task.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required(login_url='demo_login')
def update_task(request, task_id):
    """Редактирование задачи"""
    task = get_object_or_404(Task, id=task_id)

    # Проверка прав
    profile = request.user.profile
    if not (profile.is_director or profile.is_manager or task.assigned_to == request.user):
        messages.error(request, 'У вас нет прав для редактирования этой задачи')
        return redirect('reporting:demo_dashboard')

    if request.method == 'POST':
        form = SimpleTaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача успешно обновлена!')
            return redirect('reporting:demo_task_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = SimpleTaskForm(instance=task, user=request.user)

    return render(request, 'reporting/demo_task_form.html', {'form': form, 'task': task})


@login_required(login_url='reporting:demo_login')
def delete_task(request, task_id):
    """Удаление задачи"""
    task = get_object_or_404(Task, id=task_id)

    # Проверка прав
    profile = request.user.profile
    if not (profile.is_director or profile.is_manager or task.assigned_to == request.user):
        messages.error(request, 'У вас нет прав для удаления этой задачи')
        return redirect('reporting:demo_dashboard')

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Задача успешно удалена!')
        return redirect('reporting:demo_task_list')

    return render(request, 'reporting/demo_task_confirm_delete.html', {'task': task})


# API endpoints для динамических данных
@login_required(login_url='reporting:demo_login')
def get_user_tasks_stats(request):
    """API для получения статистики по задачам пользователя"""
    try:
        profile = request.user.profile

        if profile.is_director:
            total_tasks = Task.objects.count()
            completed_tasks = Task.objects.filter(status='completed').count()
        elif profile.is_manager and profile.department:
            tasks = Task.objects.filter(assigned_to__profile__department=profile.department)
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(status='completed').count()
        else:
            tasks = Task.objects.filter(assigned_to=request.user)
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(status='completed').count()

        return JsonResponse({
            'success': True,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})