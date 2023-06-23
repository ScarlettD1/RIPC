from django.forms import ModelForm

from ripc.models import Organization


# Класс формы добавления организации
class RegisterOrgForm(ModelForm):
    # класс с подключаемой моделью организации и необходимыми полями
    class Meta:
        model = Organization
        fields = ['name', 'region']

    # Перегрузка информации полей формы, подтягиваемое с модели организации
    def __init__(self, *args, **kwargs):
        super(RegisterOrgForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
