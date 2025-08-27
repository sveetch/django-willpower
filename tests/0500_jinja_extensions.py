from jinja2 import Environment, DictLoader

from django_willpower.utils.parsing import WillpowerStringObject


def wobject_render(value, quote="\""):
    """
    Filter to render the resolved object path from a 'WillpowerStringObject' object.

    The specific render behavior here is to quote (and coerced to strin) any value that
    does not use "Willpower object" syntax and value using the syntax are never quoted
    so they are correct Python expression in rendered code.

    The quote character used on default is the double quote.

    Sample: ::
        {{ some_value|wobject_render }}

    Arguments:
        value (Any): Although this filter is done for a 'WillpowerStringObject', it
            accept anything else, just only 'WillpowerStringObject' object is rendered
            specifically.

    Keyword Arguments:
        quote (string): The character to use to surround value that is not a valid
            "Willpower object" syntax

    Returns:
        (Any): Either a string for the resolved object path for a
        'WillpowerStringObject' else just return the given value unchanded.
    """
    if not getattr(value, "is_wpower_syntax", False):
        return quote + str(value) + quote

    return value.parsed_object


def test_filter_wpower_print(caplog, load_json, settings, tmp_path):
    """
    The filter 'wobject_render' should properly render a value as expected.
    """
    loader = DictLoader({
        "debug.html": (
            "string-render: {{ value }}\n"
            "string-parsed_object: {{ value.parsed_object }}\n"
            "string-implied_import: {{ value.implied_import }}\n"
            "filter-render: {{ value|wobject_render }}\n"
        ),
        "index.html": (
            "{{ value|wobject_render }}"
        ),
        "custom.html": (
            "{{ value|wobject_render(quote='#') }}"
        ),
    })

    jinja_env = Environment(loader=loader)
    jinja_env.filters["wobject_render"] = wobject_render

    template = jinja_env.get_template("index.html")

    # A value with correct Willpower object syntax is rendered as an expression
    value = WillpowerStringObject("w-object://django.conf/settings/ARTICLE_PAGINATION")
    assert template.render(value=value) == "settings.ARTICLE_PAGINATION"

    # Any other value is quoted as a string
    value = WillpowerStringObject("bidule")
    assert template.render(value=value) == "\"bidule\""

    # Quote character can be customized
    template = jinja_env.get_template("custom.html")
    value = WillpowerStringObject("bidule")
    assert template.render(value=value) == "#bidule#"
