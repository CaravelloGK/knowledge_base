from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reporting.models import Department, UserProfile, Task
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Create demo data for the reporting system'

    def handle(self, *args, **options):
        # Очистка старых данных
        Task.objects.all().delete()
        UserProfile.objects.all().delete()
        Department.objects.all().delete()

        # Создание подразделений
        dev_dept = Department.objects.create(name="Разработка")
        qa_dept = Department.objects.create(name="Тестирование")
        design_dept = Department.objects.create(name="Дизайн")

        # Создание пользователей
        users_data = [
            ('director', 'Директор', None, 'director'),
            ('dev_manager', 'Менеджер Разработки', dev_dept, 'manager'),
            ('qa_manager', 'Менеджер Тестирования', qa_dept, 'manager'),
            ('designer1', 'Дизайнер 1', design_dept, 'employee'),
            ('developer1', 'Разработчик 1', dev_dept, 'employee'),
            ('tester1', 'Тестировщик 1', qa_dept, 'employee'),
        ]

        for username, full_name, department, role in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': full_name.split()[0], 'last_name': ' '.join(full_name.split()[1:])}
            )
            if created:
                user.set_password('demo123')
                user.save()

            UserProfile.objects.create(user=user, department=department, role=role)

        # Создание демо-задач
        tasks_data = [
            ("Разработать модуль авторизации", dev_dept, 'developer1', -5, 7),
            ("Протестировать API endpoints", qa_dept, 'tester1', -3, 5),
            ("Создать дизайн главной страницы", design_dept, 'designer1', -1, 10),
            ("Исправить баг в расчетах", dev_dept, 'developer1', -2, 3),
            ("Подготовить документацию", dev_dept, 'developer1', 0, 14),
        ]

        for desc, dept, username, days_ago, deadline_days in tasks_data:
            user = User.objects.get(username=username)
            received_date = timezone.now().date() + timedelta(days=days_ago)
            planned_deadline = received_date + timedelta(days=deadline_days)

            Task.objects.create(
                description=desc,
                received_date=received_date,
                planned_deadline=planned_deadline,
                category='development' if dept == dev_dept else 'testing' if dept == qa_dept else 'design',
                task_type='feature',
                customer="Внутренний",
                assigned_to=user,
                status='completed' if days_ago < -7 else 'in_progress'
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Демо-данные успешно созданы!\n'
                'Логины: director, dev_manager, qa_manager, designer1, developer1, tester1\n'
                'Пароль для всех: demo123'
            )
        )