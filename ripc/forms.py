from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from ripc.models import Expert


class RegisterUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        fields_expert = ['region', 'org', 'subject', 'third_check']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
