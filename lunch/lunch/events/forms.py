from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Event, Order


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['store']
        widgets = {'store': forms.HiddenInput}

    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', submit_title))


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['item', 'notes']

    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].empty_label = None
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', submit_title))
