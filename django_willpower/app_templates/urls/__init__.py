from django.urls import path, include

app_name = "{{ app }}"


urlpatterns = [
{% for model_inventory in inventories %}    path("{{ model_inventory.module_name }}/", include("{{ app }}.urls.{{ model_inventory.module_name }}")),{% if not loop.last %}
{% endif %}{%- endfor %}
]

