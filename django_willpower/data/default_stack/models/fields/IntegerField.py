{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.IntegerField(
        _("{{ field.label }}"),
        {{ utils.attribute_value_coerced_number('default', field.default, field.nullable) }}{% if field.min_value or field.max_value %}
        {% if field.required %}blank=False,{% else %}blank=True,{% endif %}
        validators=[{% if field.min_value %}MinValueValidator({{ field.min_value }}),{% endif %}{% if field.min_value and field.max_value %} {% endif %}{% if field.max_value %}MaxValueValidator({{ field.max_value }}){% endif %}],{% endif %}{% if field.unique %}
        unique=True,{% endif %}{% if field.nullable %}
        null=True,{% endif %}
    )