{% import '_utils.jinja' as utils %}import pytest

from django.core.exceptions import ValidationError
from django.utils import timezone

import {{ app.code }}.models as app_models
import {{ app.code }}.factories as app_factories
{% for field in model_inventory.modelfields %}{% if field.choices_list %}from {{ app.code }}.choices import get_{{ field.name }}_default
{% endif %}{% endfor %}
{% set default_field = model_inventory.string_representation %}
def test_basic(db):
    """
    Basic model validation with required fields should not fail
    """
    obj = app_models.{{ model_inventory.name }}({% for field in model_inventory.modelfields %}{% if field.required %}
        {{ field.name }}={{ utils.test_value(field) }},{% endif %}{% endfor %}
    )
    obj.full_clean()
    obj.save()

    assert app_models.{{ model_inventory.name }}.objects.filter({{ default_field }}="Foo").count() == 1
    assert obj.{{ default_field }} == "Foo"
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

    assert excinfo.value.message_dict == {
        "heurist_id": ["This field cannot be blank."],
        "langage": ["This field cannot be blank."],
    }


def test_factory_creation(db):
    """
    Factory should correctly create a new object without any errors
    """
    obj = app_factories.{{ model_inventory.name }}Factory({{ default_field }}="foo")
    assert obj.{{ default_field }} == "foo"
