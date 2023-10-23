from django import forms

from core.models import Xodimlar


class XodimlarForm(forms.ModelForm):
    class Meta:
        model = Xodimlar
        fields = '__all__'
