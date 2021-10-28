from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm, ChangeForm, ResetForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class ChangePassword(CreateView):
    form_class = ChangeForm
    success_url = reverse_lazy('users:change_done')
    template_name = 'users/password_change_form.html'


class ResetPassword(CreateView):
    form_class = ResetForm
    success_url = reverse_lazy('users:reset_done')
    template_name = 'users/password_reset_form.html'


class PasswordConfirm(CreateView):
    success_url = reverse_lazy('users:complete')
    template_name = 'users/password_reset_confirm.html'
