{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.CharField(
        _("{{ field.label }}"),
        {{ utils.attribute_value_coerced_string('default', field.default) }}
        {% if field.required %}blank=False,{% else %}blank=True,{% endif %}
        {% if not field.max_value %}max_length=255,{% else %}max_length={{ field.max_value }},{% endif %}{% if field.unique %}
        unique=True,{% endif %}{% if field.nullable %}
        null=True,{% endif %}
    )