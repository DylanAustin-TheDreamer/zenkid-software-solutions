from django import forms
from .models import Order, Message
import re

class OrderForm(forms.ModelForm):
    number = forms.CharField(
        required=True,
        error_messages={'required': 'Please use only digits and select your country contact code.'}
    )
    email = forms.EmailField(
        required=True,
        error_messages={'required': 'Please enter your email address.', 'invalid': 'Make sure you use the @ sign.'}
    )

    class Meta:
        model = Order
        fields = ['service', 'name', 'email', 'number', 'business_name', 'message']

    def clean_number(self):
        number = self.cleaned_data['number']
        if not re.match(r'^[\d\+\-\s]+$', number):
            raise forms.ValidationError("Please use only digits and select your country contact code.")
        return number
    
class MessageForm(forms.ModelForm):
    number = forms.CharField(
        required=True,
        error_messages={'required': 'Please use only digits and select your country contact code.'}
    )
    email = forms.EmailField(
        required=True,
        error_messages={'required': 'Please enter your email address.', 'invalid': 'Make sure you use the @ sign.'}
    )
    class Meta:
        model = Message
        fields = ['name', 'email', 'number', 'subject', 'message']

    def clean_number(self):
        number = self.cleaned_data['number']
        if not re.match(r'^[\d\+\-\s]+$', number):
            raise forms.ValidationError("Please use only digits and select your country contact code.")
        return number