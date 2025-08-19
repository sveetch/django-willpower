{% for model_inventory in inventories %}from .{{ model_inventory.module_name }} import {{ model_inventory.name }}IndexView, {{ model_inventory.name }}DetailView
{% endfor %}

__all__ = [
{% for model_inventory in inventories %}    "{{ model_inventory.view_basename.format('Index') }}",
    "{{ model_inventory.view_basename.format('Detail') }}",{% if not loop.last %}
{% endif %}{%- endfor %}
]

