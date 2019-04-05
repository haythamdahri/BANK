from django import forms
import re

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={'placeholder': 'Email...', 'class': 'form-control'}),
        required=True)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe...', 'class': 'form-control'}),
        required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if re.match(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', email, re.I) is None:
            raise forms.ValidationError('Email invalide')
        return email
