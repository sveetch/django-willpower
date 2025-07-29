{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.DateTimeField(
        _("{{ field.label }}"),
        max_length=255,{% if field.unique %}
        unique=True,{% endif %}{% if field.required %}
        blank=False,{% endif %}{% if field.nullable %}
        null=True,{% endif %}{% if field.auto_creation or field.auto_update %}
        default=timezone.now,{% else %}
        default=None,{% endif %}
    )