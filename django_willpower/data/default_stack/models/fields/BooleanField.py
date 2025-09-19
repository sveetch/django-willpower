{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.BooleanField(
        _("{{ field.label }}"),
        {{ utils.attribute_bool_or_string('default', field.default) }}
        {% if field.required %}blank=False,{% else %}blank=True,{% endif %}{% if field.nullable %}
        null=True,{% endif %}
    )