from crispy_forms.helper import FormHelper
from django.forms import ModelForm
from ripc.models import Expert


class RegisterExpertForm(ModelForm):
    class Meta:
        model = Expert
        fields = ['surname', 'organization', 'referee', 'subject']

    def __init__(self, *args, **kwargs):
        super(RegisterExpertForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        for field in ['surname', 'organization', 'referee', 'subject']:
            self.fields[field].required = False
