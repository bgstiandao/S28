from django import forms
from web.forms.bootstrap import BootstrapForm
from web import models

class IssuesModelForm(BootstrapForm,forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ['project','creator','create_datetime','last_update_datetime']
