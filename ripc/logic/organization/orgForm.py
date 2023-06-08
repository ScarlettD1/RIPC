from django.forms import ModelForm

from ripc.models import Organization


class RegisterOrgForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'region']

    def __init__(self, *args, **kwargs):
        super(RegisterOrgForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
