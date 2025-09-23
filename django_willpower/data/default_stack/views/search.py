from haystack.query import RelatedSearchQuerySet
from haystack.generic_views import SearchView

from ..forms import GlobalSearchForm


class GlobalSearchView(SearchView):
    """
    View to implement search for indexed Atoum models.
    """
    template_name = "{{ app.code }}/search/results.html"
    form_class = GlobalSearchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.method == "GET":
            # Add some arguments to notify that some fields are empty
            # TODO: Usage of these args (from the crispy layout) should have a test
            # coverage
            kwargs.update({
                "empty_query": not self.request.GET.get("q"),
                "empty_models": not self.request.GET.get("models"),
            })

        return kwargs

    def get_queryset(self):
        """
        Use a ``RelatedSearchQuerySet`` so we can use ``select_related()`` when loading
        model objects from search results.
        """
        if self.queryset is None:
            self.queryset = RelatedSearchQuerySet()
        return self.queryset
