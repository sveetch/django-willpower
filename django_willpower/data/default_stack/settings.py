{% for model_inventory in inventories %}
# Pagination limit for model '{{ model_inventory.name }}'
{{ model_inventory.name|upper }}_LIST_PAGINATION = 20
{% endfor %}
