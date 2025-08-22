from django import forms

from ..models import {{ model_inventory.name }}


class {{ model_inventory.admin_name }}Form(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = {{ model_inventory.name }}
