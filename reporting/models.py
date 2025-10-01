from django.contrib.auth.models import User
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название подразделения")

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
    ]

    CATEGORY_CHOICES = [
        ('development', 'Разработка'),
        ('testing', 'Тестирование'),
        ('design', 'Дизайн'),
        ('documentation', 'Документация'),
    ]

    TYPE_CHOICES = [
        ('bug', 'Исправление ошибки'),
        ('feature', 'Новая функция'),
        ('improvement', 'Улучшение'),
        ('urgent', 'Срочная задача'),
    ]

    received_date = models.DateField(verbose_name="Дата поступления задачи")
    planned_deadline = models.DateField(verbose_name="Плановый срок завершения")
    actual_deadline = models.DateField(null=True, blank=True, verbose_name="Фактический срок завершения")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория задачи")
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Тип задачи")
    customer = models.CharField(max_length=100, verbose_name="Заказчик", default="Внутренний")
    description = models.TextField(verbose_name="Описание задачи")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Исполнитель")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-received_date']

    def __str__(self):
        return f"{self.description[:50]}..."

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.planned_deadline < timezone.now().date() and self.status != 'completed'


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('employee', 'Работник'),
        ('manager', 'Руководитель'),
        ('director', 'Директор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_director(self):
        return self.role == 'director'