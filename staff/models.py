from django.db import models
from django.urls import reverse


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование")
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL,
                                blank=True, null=True,
                                verbose_name="Руководитель",
                                related_name='managed_departments')  # Добавляем related_name
    parent_department = models.ForeignKey('self', on_delete=models.CASCADE,
                                          blank=True, null=True,
                                          verbose_name="Родительское подразделение",
                                          related_name='child_departments')  # Добавляем related_name

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"

    def __str__(self):
        return self.name

    def get_children(self):
        return self.child_departments.all()

    def get_employees(self):
        return self.employees.all()  # Используем related_name

    def get_absolute_url(self):
        return reverse('staff:department_detail', kwargs={'pk': self.pk})


class Employee(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="ФИО")
    position = models.CharField(max_length=100, verbose_name="Должность")
    phone = models.CharField(max_length=20, blank=True, null=True,
                             verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    manager = models.ForeignKey('self', on_delete=models.SET_NULL,
                                blank=True, null=True,
                                verbose_name="Руководитель",
                                related_name='subordinates')  # Добавляем related_name
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,
                                   blank=True, null=True,
                                   verbose_name="Подразделение",
                                   related_name='employees')  # Добавляем related_name

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"{self.full_name} ({self.position})"

    def get_absolute_url(self):
        return reverse('staff:employee_detail', kwargs={'pk': self.pk})

    def get_subordinates(self):
        return self.subordinates.all()