from django.conf import settings
from django.views.generic import ListView
from django.views.generic import DetailView

from ..models import {{ model_inventory.name }}


class {{ model_inventory.view_basename.format('Index') }}(ListView):
    """
    {{ model_inventory.name }} index view.
    """
    model = {{ model_inventory.name }}
    template_name = "{{ app }}/{{ model_inventory.module_name }}/index.html"
    paginate_by = 42

    def get_queryset(self):
        return self.model.objects.order_by("id")


class {{ model_inventory.view_basename.format('Detail') }}(DetailView):
    """
    {{ model_inventory.name }} detail view.
    """
    model = {{ model_inventory.name }}
    pk_url_kwarg = "{{ model_inventory.module_name }}_pk"
    template_name = "{{ app }}/{{ model_inventory.module_name }}/detail.html"
    context_object_name = "{{ model_inventory.module_name }}_object"

    def get_queryset(self):
        return self.model.objects.all()

