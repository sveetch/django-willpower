{% import '_utils.jinja' as utils %}
    {{ field.name }} = models.ManyToManyField(
        {{ field.target|wobject_render|str_format(appname=model_inventory.app.code) }},
        {% if field.required %}blank=False,{% else %}blank=True,{% endif %}
        verbose_name=_("{{ field.label }}"),{% if field.related_name %}
        related_name="{{ field.related_name }}s",{% endif %}
    )