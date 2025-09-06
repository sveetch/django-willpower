from jinja2 import Environment, DictLoader

from django_willpower.utils.parsing import WillpowerStringObject
from django_willpower.utils.jinja import str_format, wobject_render


def test_filter_str_format():
    """
    The filter 'str_format' should implement 'str.format()' correctly.
    """
    loader = DictLoader({
        "args_only.html": (
            "{{ value|str_format(foo, bar) }}"
        ),
        "args_asterisks.html": (
            "{{ value|str_format(*payload) }}"
        ),
        "kwargs_only.html": (
            "{{ value|str_format(foo=foo, bar=bar) }}"
        ),
        "kwargs_asterisks.html": (
            "{{ value|str_format(**payload) }}"
        ),
        "args_kwargs_mixed.html": (
            "{{ value|str_format(foo, bar=bar) }}"
        ),
        "args_kwargs_asterisks.html": (
            "{{ value|str_format(*args, **kwargs) }}"
        ),
    })

    jinja_env = Environment(loader=loader)
    jinja_env.filters["str_format"] = str_format

    template = jinja_env.get_template("args_only.html")
    assert template.render(
        value="foo={}; bar={}",
        foo="Foo!",
        bar="Bar!",
    ) == "foo=Foo!; bar=Bar!"

    template = jinja_env.get_template("args_asterisks.html")
    assert template.render(
        value="foo={}; bar={}",
        payload=[
            "Foo!",
            "Bar!",
        ],
    ) == "foo=Foo!; bar=Bar!"

    template = jinja_env.get_template("kwargs_only.html")
    assert template.render(
        value="foo={foo}; bar={bar}",
        foo="Foo!",
        bar="Bar!",
    ) == "foo=Foo!; bar=Bar!"

    template = jinja_env.get_template("kwargs_asterisks.html")
    assert template.render(
        value="foo={foo}; bar={bar}",
        payload={
            "foo": "Foo!",
            "bar": "Bar!",
        },
    ) == "foo=Foo!; bar=Bar!"

    template = jinja_env.get_template("args_kwargs_mixed.html")
    assert template.render(
        value="foo={}; bar={bar}",
        foo="Foo!",
        bar="Bar!",
    ) == "foo=Foo!; bar=Bar!"

    template = jinja_env.get_template("args_kwargs_asterisks.html")
    assert template.render(
        value="foo={}; bar={bar}",
        args=["Foo!"],
        kwargs={"bar": "Bar!"},
    ) == "foo=Foo!; bar=Bar!"


def test_filter_wpower_print():
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
