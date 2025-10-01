from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    # Главная страница - редирект на логин или дашборд
    path('', views.home_redirect, name='home'),

    # Аутентификация
    path('login/', views.demo_login, name='demo_login'),
    path('logout/', views.demo_logout, name='demo_logout'),

    # Основные страницы
    path('dashboard/', views.dashboard, name='demo_dashboard'),
    path('tasks/', views.task_list, name='demo_task_list'),

    # Управление задачами
    path('tasks/create/', views.create_task, name='demo_create_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='demo_update_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='demo_delete_task'),
    path('tasks/quick-create/', views.quick_create_task, name='demo_quick_create_task'),

    # API endpoints
    path('api/user-stats/', views.get_user_tasks_stats, name='api_user_stats'),
]