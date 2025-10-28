from haystack.forms import ModelSearchForm

from ..form_helpers import AdvancedSearchFormHelper
from ..utils.text import normalize_text
from ..models import ({% for model_inventory in inventories %}
    {{ model_inventory.name }}{% if not loop.last %},{% endif %}{% endfor %}
)


class GlobalSearchForm(ModelSearchForm):
    """
    Form to search on all enabled Atoum models.
    """

    def __init__(self, *args, **kwargs):
        empty_query = kwargs.pop("empty_query", False)
        empty_models = kwargs.pop("empty_models", False)

        super().__init__(*args, **kwargs)

        # We don't want label since we use a group inline layout
        self.fields["q"].label = False
        self.fields["models"].label = False

        self.helper = AdvancedSearchFormHelper(
            empty_query=empty_query,
            empty_models=empty_models,
        )

    def search(self):
        """
        We don't keep the base queryset from inherited ModelSearchForm since it starts
        with an 'auto_query' that is not efficient with partial search. However this
        drops the feature of some operator like ``-`` to negate keywords.
        """
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get("q"):
            return self.no_query_found()

        # Search on main content with normalized query
        sqs = self.searchqueryset.filter(text=normalize_text(self.cleaned_data["q"]))

        # Enable all discovered model indexes from enabled applications
        sqs = sqs.models(*self.get_models())

        if self.load_all:
            # Get model objects from search result references
            sqs = sqs.load_all()

            # Chaining model results{% for model_inventory in inventories %}
            sqs = sqs.load_all_queryset(
                {{ model_inventory.name }},
                {{ model_inventory.name }}.objects.all()
            )
            {% endfor %}
        return sqs

