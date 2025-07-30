from django.contrib import admin

from ..models import {{ model_inventory.name }}


@admin.register({{ model_inventory.name }})
class {{ model_inventory.admin_name }}(admin.ModelAdmin):
    """
    {{ model_inventory.name }} admin.
    """{% if model_inventory.admin_list_display %}
    list_display = ["{{ model_inventory.admin_list_display|join('", "') }}"]{% endif %}{% if model_inventory.readonly_fields %}
    readonly_fields = ["{{ model_inventory.readonly_fields|join('", "') }}"]{% endif %}{% if model_inventory.default_order %}
    ordering = ["{{ model_inventory.default_order|join('", "') }}"]{% endif %}{% if model_inventory.list_filter %}
    list_filter = ["{{ model_inventory.list_filter|join('", "') }}"]{% endif %}{% if model_inventory.search_fields %}
    search_fields = ["{{ model_inventory.search_fields|join('", "') }}"]{% endif %}{% if model_inventory.admin_inline_models %}
    inlines = [{{ model_inventory.admin_inline_models|join(', ') }}]{% endif %}{% if model_inventory.prepopulated_fields %}
    prepopulated_fields = {{ model_inventory.prepopulated_fields|tojson }}{% endif %}
