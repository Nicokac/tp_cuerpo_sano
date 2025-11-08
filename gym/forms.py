from __future__ import annotations

from django import forms
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
