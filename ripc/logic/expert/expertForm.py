from crispy_forms.helper import FormHelper
from django.forms import ModelForm
from ripc.models import Expert


# Класс формы регистрации эксперта
class RegisterExpertForm(ModelForm):
    # класс с подключаемой моделью эксперта и необходимыми полями
    class Meta:
        model = Expert
        fields = ['surname', 'organization', 'referee', 'subject']

    # Перегрузка информации полей формы, подтягиваемое с модели эксперта
    def __init__(self, *args, **kwargs):
        super(RegisterExpertForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        for field in ['surname', 'organization', 'referee', 'subject']:
            self.fields[field].required = False
