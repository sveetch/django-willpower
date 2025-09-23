from django.conf import settings

from haystack.fields import (
    CharField as OriginalCharField,
    EdgeNgramField as OriginalEdgeNgramField
)


class DebuggingField:
    """
    A custom search field for CharField which is able to print the rendered indexes
    content when it is allowed so from ``settings.ATOUM_INDEXES_DEBUG``.
    """

    def prepare_template(self, obj):
        """
        Render object index then print it out if settings ``HAYSTACK_INDEXES_DEBUG`` is
        enabled.
        """
        if not getattr(settings, "HAYSTACK_INDEXES_DEBUG", None):
            return super().prepare_template(obj)
        else:
            rendered = super().prepare_template(obj)
            title = "_____ <{}:{}> ".format(obj._meta.model.__name__, str(obj.id))
            print(title + ("_" * (60 - len(title))))
            print(rendered)
            return rendered


class CharField(DebuggingField, OriginalCharField):
    """
    A custom search field for CharField which is able to print the rendered object
    indexes when index debug is enabled
    """
    pass


class EdgeNgramField(DebuggingField, OriginalEdgeNgramField):
    """
    A custom search field for EdgeNgramField which is able to print the rendered object
    indexes when index debug is enabled.
    """
    pass
