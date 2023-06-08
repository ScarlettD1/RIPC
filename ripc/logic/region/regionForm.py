from crispy_forms.helper import FormHelper
from django.forms import ModelForm, forms

from ripc.models import Region


class RegisterRegionForm(ModelForm):
    class Meta:
        model = Region
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError('Название должно содержать не менее 3 символов')
        if name.isnumeric():
            raise forms.ValidationError('Название не может состоять только из цифр')
        return name

    def __init__(self, *args, **kwargs):
        super(RegisterRegionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
