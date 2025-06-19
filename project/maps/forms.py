from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

from . import models


class CustomAuthForm(AuthenticationForm):
    error_css_class = "is-invalid"

    username = forms.CharField(
        widget=TextInput(attrs={"class": "validate", "placeholder": "Username"}),
        label="",
    )
    password = forms.CharField(
        widget=PasswordInput(attrs={"placeholder": "Password"}),
        label="",
    )


class TripForm(forms.ModelForm):
    error_css_class = "is-invalid"

    class Meta:
        model = models.Trip
        fields = ["title", "description", "blog_category", "start_date", "end_date"]

    def clean(self):
        cleaned = super().clean()

        started = cleaned.get("start_date")
        ended = cleaned.get("end_date")

        if ended and started and ended < started:
            self.add_error(
                "end_date", "The end date of trip must be later than the start date."
            )

        return cleaned


class GetFitByDateForm(forms.Form):
    error_css_class = "is-invalid"

    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)

    def clean(self):
        cleaned = super().clean()

        started = cleaned.get("start_date")
        ended = cleaned.get("end_date")

        if ended and started and ended < started:
            self.add_error(
                "end_date", "The end date of trip must be later than the start date."
            )

        return cleaned
