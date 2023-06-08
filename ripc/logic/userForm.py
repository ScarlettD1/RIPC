from crispy_forms.helper import FormHelper
from django.forms import ModelForm
from django.contrib.auth.models import User


class RegisterUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'username', 'last_name', 'password', 'email']
        labels = {
            'username': 'Логин',
        }

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['username'].help_text = 'Только буквы, цифры и символы @ . + - _.'
        for field in ['first_name', 'username', 'last_name', 'password', 'email']:
            self.fields[field].required = False
        self.fields['username'].lable = 'Логин'
