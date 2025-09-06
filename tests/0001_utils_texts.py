import pytest

from django_willpower.utils.texts import text_to_pascal_case, text_to_snake_case


@pytest.mark.parametrize("value, expected", [
    ("Foo", "Foo"),
    ("Foo bar", "FooBar"),
    ("Foo-bar", "FooBar"),
    ("foo-bar zip", "FooBarZip"),
])
def test_text_to_pascal_case(value, expected):
    """
    String should be turned to a proper 'PascalCase' case.
    """
    assert text_to_pascal_case(value) == expected


@pytest.mark.parametrize("value, expected", [
    ("Foo", "foo"),
    ("Foo bar", "foo_bar"),
    ("Foo-bar", "foo_bar"),
    ("foo-bar zip", "foo_bar_zip"),
])
def test_text_to_snake_case(value, expected):
    """
    String should be turned to a proper 'snake_case' case.
    """
    assert text_to_snake_case(value) == expected
