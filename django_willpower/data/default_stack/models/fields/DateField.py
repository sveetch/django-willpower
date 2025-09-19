{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.DateField(
        _("{{ field.label }}"),
        max_length=255,
        {% if field.required %}blank=False,{% else %}blank=True,{% endif %}{% if field.unique %}
        unique=True,{% endif %}{% if field.nullable %}
        null=True,{% endif %}{% if field.auto_creation or field.auto_update %}
        default=timezone.now,{% elif field.nullable %}
        default=None,{% endif %}
    )
