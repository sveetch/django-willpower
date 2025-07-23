{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.DateTimeField(
        _("{{ field.name }}"),
        {{ utils.attribute_bool_or_string('default', field.default) }}
        max_length=255,{% if field.unique %}
        unique=True,{% endif %}{% if field.required %}
        blank=False,{% endif %}{% if field.nullable %}
        null=True,{% endif %}
    )