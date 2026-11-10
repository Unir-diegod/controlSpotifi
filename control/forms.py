from django import forms
from django.utils import timezone

from .models import Member, Payment


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["name", "monthly_fee"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del integrante",
                    "autocomplete": "off",
                }
            ),
            "monthly_fee": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "step": 1}
            ),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["member", "amount", "paid_at", "method"]
        widgets = {
            "member": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "step": 1,
                    "placeholder": "10.000",
                }
            ),
            "paid_at": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": "form-control", "type": "date"},
            ),
            "method": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Member.objects.filter(is_active=True)
        self.fields["paid_at"].initial = timezone.localdate()
