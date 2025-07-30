{% for model_inventory in inventories %}from .{{ model_inventory.module_name }} import {{ model_inventory.name }}Admin
{% endfor %}

__all__ = [
{% for model_inventory in inventories %}    "{{ model_inventory.name }}Admin",{% if not loop.last %}
{% endif %}{%- endfor %}
]

