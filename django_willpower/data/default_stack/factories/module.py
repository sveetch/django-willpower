{% import '_utils.jinja' as utils %}import factory

from django.conf import settings
from django.utils import timezone

from ..models import {{ model_inventory.name }}{% for field in model_inventory.modelfields %}{% if field.choices_list %}
from ..choices import get_{{ field.name }}_default{% endif %}{% endfor %}
{% for field in model_inventory.modelfields %}{% if field.kind in ['ForeignKey', 'ManyToManyField'] %}
from {{ utils.get_subfactory_modulepath(app.code, field.target.parsed_object) }} import {{ utils.get_subfactory_modulename(app.code, field.target.parsed_object) }}{% endif %}{% endfor %}


class {{ model_inventory.name }}Factory(factory.django.DjangoModelFactory):
    """
    {{ model_inventory.name }} factory.
    """
{% for field in model_inventory.modelfields %}{% if field.kind not in ['DateField', 'DateTimeField', 'TimeField', 'ManyToManyField'] %}{% include "factories/fields/{}.py"|str_format(field.kind) %}
{% endif %}{% endfor %}{% for field in model_inventory.modelfields %}{% if field.kind in ['DateField', 'DateTimeField', 'TimeField', 'ManyToManyField'] %}
{% include "factories/fields/{}.py"|str_format(field.kind) %}
{% endif %}{% endfor %}
    class Meta:
        model = {{ model_inventory.name }}
        skip_postgeneration_save = True

