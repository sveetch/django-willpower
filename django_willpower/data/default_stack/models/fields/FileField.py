{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.FileField(
        _("{{ field.label }}"),
        {{ utils.attribute_value_coerced_string('default', field.default) }}
        upload_to="{{ model_inventory.app.code }}/{{ model_inventory.module_name }}/{{ field.name }}/%y/%m",
        max_length=255,{% if field.unique %}
        unique=True,{% endif %}{% if field.required %}
        blank=False,{% endif %}{% if field.nullable %}
        null=True,{% endif %}
    )