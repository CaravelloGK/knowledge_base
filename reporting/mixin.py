# reports/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class DemoLoginRequiredMixin(LoginRequiredMixin):
    """Миксин для проверки аутентификации в демо-версии"""
    login_url = 'demo_login'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url + f'?next={request.path}')
        return super().dispatch(request, *args, **kwargs)