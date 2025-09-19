{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.CharField(
        _("{{ field.label }}"),
        choices=get_{{ field.name }}_choices(),
        default=get_{{ field.name }}_default(),
        {% if field.required %}blank=False,{% else %}blank=True,{% endif %}
        {% if not field.max_value %}max_length=255,{% else %}max_length={{ field.max_value }},{% endif %}{% if field.unique %}
        unique=True,{% endif %}{% if field.nullable %}
        null=True,{% endif %}
    )