{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.EmailField(
        _("{{ field.label }}"),
        {{ utils.attribute_value_coerced_string('default', field.default, field.nullable) }}
        {% if field.required %}blank=False,{% else %}blank=True,{% endif %}
        max_length=255,{% if field.unique %}
        unique=True,{% endif %}{% if field.nullable %}
        null=True,{% endif %}
    )