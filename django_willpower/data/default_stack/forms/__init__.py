{% for model_inventory in inventories %}from .{{ model_inventory.module_name }} import {{ model_inventory.admin_name }}Form
{% endfor %}

__all__ = [
{% for model_inventory in inventories %}    "{{ model_inventory.admin_name }}Form",{% if not loop.last %}
{% endif %}{%- endfor %}
]

