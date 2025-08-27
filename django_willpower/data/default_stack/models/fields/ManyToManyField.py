{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.ManyToManyField(
        "{{ field.target.parsed_object.format(appname=model_inventory.app.code)|lower }}",
        verbose_name=_("{{ field.label }}"),{% if field.related_name %}
        related_name="{{ field.related_name }}s",{% endif %}{% if not field.required %}
        blank=True,{% endif %}
    )