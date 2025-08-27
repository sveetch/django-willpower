{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.ForeignKey(
        "{{ field.target.parsed_object.format(appname=model_inventory.app.code)|lower }}",
        on_delete={% if field.on_delete %}{{ field.on_delete }}{% else %}models.CASCADE{% endif %},
        verbose_name=_("{{ field.label }}"),{% if field.related_name %}
        related_name="{{ field.related_name }}",{% endif %}{% if field.unique %}
        unique=True,{% endif %}{% if field.required %}
        blank=False,{% else %}
        null=True,
        default=None,{% endif %}
    )