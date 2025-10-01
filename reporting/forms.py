from django import forms
from .models import Task
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column


class SimpleTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['received_date', 'planned_deadline', 'actual_deadline',
                  'category', 'task_type', 'customer', 'description', 'status']
        widgets = {
            'received_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'task_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Сохранить', css_class='btn-primary'))


class QuickTaskForm(SimpleTaskForm):
    """Упрощенная форма для быстрого создания задач"""

    class Meta(SimpleTaskForm.Meta):
        fields = ['description', 'planned_deadline', 'category', 'task_type']