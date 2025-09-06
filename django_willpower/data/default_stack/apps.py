from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class {{ app.get_appcode_pascal_case() }}Config(AppConfig):
    name = "{{ app.get_appcode_snake_case() }}"
    verbose_name = _("{{ app.name }}")
    default_auto_field = "django.db.models.AutoField"
