from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, Message, Mechanic
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
    
class MechanicForm(forms.ModelForm):
    number = forms.CharField(
        required=True,
        error_messages={'required': 'Please use only digits and select your country contact code.'}
    )
    email = forms.EmailField(
        required=True,
        error_messages={'required': 'Please enter your email address.', 'invalid': 'Make sure you use the @ sign.'}
    )

    class Meta:
        model = Mechanic
        fields = ['name', 'email', 'number', 'business_name', 'message']

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
        fields = ['name', 'email', 'number', 'subject', 'order_ref', 'message']

    def clean_number(self):
        number = self.cleaned_data['number']
        if not re.match(r'^[\d\+\-\s]+$', number):
            raise forms.ValidationError("Please use only digits and select your country contact code.")
        return number


class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    business_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'business_name', 'password1', 'password2']

    def save(self, commit=True):
        from .models import CustomerProfile

        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            CustomerProfile.objects.update_or_create(
                user=user,
                defaults={'business_name': self.cleaned_data.get('business_name', '').strip()},
            )

        return user