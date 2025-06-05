from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput


class CustomAuthForm(AuthenticationForm):
    error_css_class = "is-invalid"

    username = forms.CharField(
        widget=TextInput(attrs={"class": "validate", "placeholder": "Username"}),
        label=''
    )
    password = forms.CharField(
        widget=PasswordInput(attrs={"placeholder": "Password"}),
        label='',
    )
