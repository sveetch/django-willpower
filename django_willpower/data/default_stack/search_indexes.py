from haystack import indexes

from .models import ({% for model_inventory in inventories %}
    {{ model_inventory.name }}{% if not loop.last %},{% endif %}{% endfor %}
)
from .search_fields import EdgeNgramField
{% for model_inventory in inventories %}

class {{ model_inventory.name }}SearchIndex(indexes.SearchIndex, indexes.Indexable):
    text = EdgeNgramField(
        document=True,
        use_template=True,
        template_name=(
            "{{ model_inventory.app.code }}/{{ model_inventory.module_name }}/search_field_index.txt"
        )
    )

    def get_model(self):
        return {{ model_inventory.name }}
{% endfor %}
