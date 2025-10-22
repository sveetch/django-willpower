import factory

from django.conf import settings
from django.utils import timezone

from ..models import {{ model_inventory.name }}{% for field in model_inventory.modelfields %}{% if field.choices_list %}
from ..choices import get_{{ field.name }}_default{% endif %}{% endfor %}

class {{ model_inventory.name }}Factory(factory.django.DjangoModelFactory):
    """
    {{ model_inventory.name }} factory.
    """
{% for field in model_inventory.modelfields %}{% if field.kind not in ['DateField', 'DateTimeField', 'TimeField'] %}{% include "factories/fields/{}.py"|str_format(field.kind) %}
{% endif %}{% endfor %}{% for field in model_inventory.modelfields %}{% if field.kind in ['DateField', 'DateTimeField', 'TimeField'] %}
{% include "factories/fields/{}.py"|str_format(field.kind) %}
{% endif %}{% endfor %}
    class Meta:
        model = {{ model_inventory.name }}
        skip_postgeneration_save = True

