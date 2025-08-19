from django import forms

# from dal import autocomplete

from ..models import {{ model_inventory.name }}


# class {{ model_inventory.admin_name }}Form(autocomplete.FutureModelForm):
class {{ model_inventory.admin_name }}Form(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = {{ model_inventory.name }}
        # widgets = {
        #     "{{ item }}": autocomplete.TaggitSelect2("{{ app }}:{{ item }}-autocomplete"),
        # }
