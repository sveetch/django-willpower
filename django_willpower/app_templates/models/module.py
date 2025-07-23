from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone


class {{ model_inventory.name }}(models.Model):
    """
    {{ model_inventory.name }} model.

    Attributes:
{% for field in model_inventory.modelfields %}        {{ field.name }} ({{ field.kind }}):
{% endfor %}
    """
{% for field in model_inventory.modelfields %}{% include field.modelfield_template %}
{% endfor %}
    class Meta:
        verbose_name = _("{{ model_inventory.name }}")
        verbose_name_plural = _("{{ model_inventory.name }}s")
        ordering = [
            "title",
        ]
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
        return reverse("{{ model_inventory.app }}:{{ model_inventory.module_name }}-detail", kwargs={
            "{{ model_inventory.module_name }}_slug": self.slug,
        })

    {% if False %}
    def save(self, *args, **kwargs):
        # Auto update 'modified' value on each save
        self.modified = timezone.now()

        super().save(*args, **kwargs)
    {% endif %}
