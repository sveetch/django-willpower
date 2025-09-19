from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

{% for field in model_inventory.modelfields %}{% if field.choices_list %}
from ..choices import get_{{ field.name }}_choices, get_{{ field.name }}_default{% endif %}{% endfor %}


class {{ model_inventory.name }}(models.Model):
    """
    {{ model_inventory.name }} model.

    Attributes:
{% for field in model_inventory.modelfields %}        {{ field.name }} ({{ field.kind }}): {% if field.required %}Required{% else %}Optional{% endif %}
{% endfor %}    """
{% for field in model_inventory.modelfields %}{% include field.modelfield_template %}
{% endfor %}
    {% if model_inventory.string_representation %}TITLE_FIELD_DISPLAY = {% if model_inventory.string_representation is string -%}"{{ model_inventory.string_representation }}"{% else %}{{ model_inventory.string_representation|tojson }}{%- endif %}{%- endif %}

    class Meta:
        verbose_name = _("{{ model_inventory.name }}")
        verbose_name_plural = _("{{ model_inventory.name }}s"){% if model_inventory.default_order %}
        ordering = [{% for fieldname in model_inventory.default_order %}"{{ fieldname }}",{% endfor %}]
{% endif %}
    {% if model_inventory.string_representation %}
    def __str__(self):
        return self.get_display_title() or gettext("Empty")

    def get_display_title(self):
        return {% if model_inventory.string_representation is string -%}
            getattr(self, self.TITLE_FIELD_DISPLAY){% else %}" ".join([getattr(self, k) for k in self.TITLE_FIELD_DISPLAY])
        {%- endif %}
    {% endif %}
    def get_absolute_url(self):
        """
        Return absolute URL to the detail view.

        Returns:
            string: An URL.
        """
        return reverse("{{ model_inventory.app.code }}:{{ model_inventory.module_name }}-detail", kwargs={"{{ model_inventory.module_name }}_pk": self.id})

    def save(self, *args, **kwargs):
{% for field in model_inventory.modelfields %}{% if field.auto_update %}        self.{{ field.name }} = timezone.now()
{% endif %}{% endfor %}
        super().save(*args, **kwargs)

