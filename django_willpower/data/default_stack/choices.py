from django.utils.translation import gettext_lazy as _

{% for model_inventory in inventories %}{% for field in model_inventory.modelfields %}{% if field.choices_list %}
def get_{{ field.name }}_choices():
    return [{% for item in field.choices_list %}
        ("{{ item }}", _("{{ item }}")),{% endfor %}
    ]

def get_{{ field.name }}_default():
    return get_{{ field.name }}_choices()[0][0]
{% endif %}{% endfor %}{% endfor %}

