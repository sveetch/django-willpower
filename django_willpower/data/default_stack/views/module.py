from django.conf import settings
from django.views.generic import ListView
{% if not model_inventory.related_model %}from django.views.generic import DetailView{% else %}from django.views.generic.detail import SingleObjectMixin{% endif %}

from ..models import {{ model_inventory.name }}{% if model_inventory.related_model %}, {{ model_inventory.related_model }}{% endif %}


class {{ model_inventory.view_basename.format('Index') }}(ListView):
    """
    {{ model_inventory.name }} index view.
    """
    model = {{ model_inventory.name }}
    template_name = "{{ model_inventory.app.code }}/{{ model_inventory.module_name }}/index.html"
    paginate_by = settings.{{ model_inventory.name|upper }}_LIST_PAGINATION

    def get_queryset(self):
        return self.model.objects.order_by({% if model_inventory.string_representation is string -%}"{{ model_inventory.string_representation }}"{% elif model_inventory.string_representation %}{% for item in model_inventory.string_representation %}"{{ item }}"{% if not loop.last %}, {% endif %}{% endfor %}{% else %}"id"{% endif %})


{% if not model_inventory.related_model %}class {{ model_inventory.view_basename.format('Detail') }}(DetailView):
    """
    {{ model_inventory.name }} detail view.
    """
    model = {{ model_inventory.name }}
    pk_url_kwarg = "{{ model_inventory.module_name }}_pk"
    template_name = "{{ model_inventory.app.code }}/{{ model_inventory.module_name }}/detail.html"
    context_object_name = "{{ model_inventory.module_name }}_object"

    def get_queryset(self):
        return self.model.objects.all()
{% else %}class {{ model_inventory.view_basename.format('Detail') }}(SingleObjectMixin, ListView):
    """
    {{ model_inventory.name }} detail view which list {{ model_inventory.related_model }} objects relations.
    """
    model = {{ model_inventory.name }}
    reversed_model = {{ model_inventory.related_model }}
    pk_url_kwarg = "{{ model_inventory.module_name }}_pk"
    template_name = "{{ model_inventory.app.code }}/{{ model_inventory.module_name }}/detail.html"
    context_object_name = "{{ model_inventory.module_name }}_object"
    paginate_by = settings.{{ model_inventory.related_model|upper }}_LIST_PAGINATION

    def get_queryset(self):
        return self.object.{{ model_inventory.related_model|lower }}_set.order_by(
            self.reversed_model.TITLE_FIELD_DISPLAY
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.all())

        return super().get(request, *args, **kwargs)
{% endif %}
