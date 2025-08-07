from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class {{ model_inventory.name }}(models.Model):
    """
    {{ model_inventory.name }} model.

    Attributes:
{% for field in model_inventory.modelfields %}        {{ field.name }} ({{ field.kind }}): {% if field.required %}Required{% else %}Optional{% endif %}
{% endfor %}    """
{% for field in model_inventory.modelfields %}{% include field.modelfield_template %}
{% endfor %}
    class Meta:
        verbose_name = _("{{ model_inventory.name }}")
        verbose_name_plural = _("{{ model_inventory.name }}s"){% if model_inventory.default_order %}
        ordering = [{% for fieldname in model_inventory.default_order %}"{{ fieldname }}",{% endfor %}]
{% endif %}
    {% if False %}
    def __str__(self):
        return self.title
    {% endif %}
    def get_absolute_url(self):
        """
        Return absolute URL to the detail view.

        Returns:
            string: An URL.
        """
        return reverse("{{ model_inventory.app }}:{{ model_inventory.module_name }}-detail", kwargs={"{{ model_inventory.module_name }}_pk": self.id})

    def save(self, *args, **kwargs):
{% for field in model_inventory.modelfields %}{% if field.auto_update %}        self.{{ field.name }} = timezone.now()
{% endif %}{% endfor %}
        super().save(*args, **kwargs)

