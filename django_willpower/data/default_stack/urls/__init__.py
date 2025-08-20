from django.urls import path, include

app_name = "{{ app.code }}"


urlpatterns = [
{% for model_inventory in inventories %}    path("{{ model_inventory.module_name }}/", include("{{ app.code }}.urls.{{ model_inventory.module_name }}")),{% if not loop.last %}
{% endif %}{%- endfor %}
]

