from django import forms

from haystack.forms import ModelSearchForm

from ..models import {{ model_inventory.name }}
from ..form_helpers import DefaultFormHelper
from ..utils.text import normalize_text


class {{ model_inventory.admin_name }}Form(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = {{ model_inventory.name }}


class {{ model_inventory.name }}GlobalSearchForm(ModelSearchForm):
    """
    Form to search on {{ model_inventory.name }} model.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We don't want label since we use a group inline layout
        self.fields["q"].label = False

        self.helper = DefaultFormHelper()

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

        # Get model objects from search result references
        sqs = sqs.load_all()

        # Chaining model results
        sqs = sqs.load_all_queryset(
            {{ model_inventory.name }},
            {{ model_inventory.name }}.objects.all()
        )

        return sqs

