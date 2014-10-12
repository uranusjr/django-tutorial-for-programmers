from django import forms
from .models import Store
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class StoreForm(forms.ModelForm):

    class Meta:
        model = Store

    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', submit_title))
