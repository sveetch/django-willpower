{% import '_utils.jinja' as utils %}import pytest

from django.core.exceptions import ValidationError
from django.utils import timezone

import {{ app.code }}.models as app_models
import {{ app.code }}.factories as app_factories
{% for field in model_inventory.modelfields %}{% if field.choices_list %}from {{ app.code }}.choices import get_{{ field.name }}_default
{% endif %}{% endfor %}
{% set representation_field = utils.get_model_representation_string(model_inventory.string_representation) %}
{% set default_field = model_inventory.get_required_fields() | first %}
def test_basic(db):
    """
    Basic model validation with required fields should not fail
    """
    obj = app_models.{{ model_inventory.name }}({% for field in model_inventory.get_required_fields() %}
        {{ field.name }}={{ utils.test_dummy_value(field) }},{% endfor %}
    )
    obj.full_clean()
    obj.save()

    assert app_models.{{ model_inventory.name }}.objects.filter({{ default_field.name }}={{ utils.test_dummy_value(default_field) }}).count() == 1
    assert obj.{{ default_field.name }} == {{ utils.test_dummy_value(default_field) }}
    assert obj.get_absolute_url() is not None


def test_required_fields(db, settings):
    """
    Basic model validation with missing required fields should fail.
    """
    # Ensure validation message are in stable language
    settings.LANGUAGE_CODE = "en"

    obj = app_models.{{ model_inventory.name }}()

    with pytest.raises(ValidationError) as excinfo:
        obj.full_clean()

    assert excinfo.value.message_dict == {{ '{' }}{% for field in model_inventory.get_required_fields() %}
        "{{ field.name }}": ["This field cannot be blank."],{% endfor %}
    {{ '}' }}


def test_factory_creation(db):
    """
    Factory should correctly create a new object without any errors
    """
    obj = app_factories.{{ model_inventory.name }}Factory({{ representation_field }}="foo")
    assert obj.{{ representation_field }} == "foo"

