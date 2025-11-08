from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import ClassSession, Member, Payment


class GymAttendanceForm(forms.Form):
    member = forms.ModelChoiceField(
        queryset=Member.objects.filter(is_active=True).order_by("last_name", "first_name"),
        label="Miembro",
    )


class ClassAttendanceForm(forms.Form):
    class_session = forms.ModelChoiceField(
        queryset=ClassSession.objects.all().order_by("start"),
        label="Clase",
    )
    member = forms.ModelChoiceField(
        queryset=Member.objects.filter(is_active=True).order_by("last_name", "first_name"),
        label="Miembro",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now()
        self.fields["class_session"].queryset = ClassSession.objects.filter(start__gte=now).order_by("start")


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            "member",
            "membership_type",
            "date",
            "amount",
            "method",
            "status",
            "reference",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].required = False
        self.fields["date"].initial = timezone.localdate()
        self.fields["member"].queryset = Member.objects.filter(is_active=True).order_by(
            "last_name", "first_name"
        )

    def clean(self):
        cleaned_data = super().clean()
        membership_type = cleaned_data.get("membership_type")
        amount = cleaned_data.get("amount")
        if membership_type and amount in (None, ""):
            cleaned_data["amount"] = membership_type.price
        return cleaned_data


class SignupForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150)
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"]
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
