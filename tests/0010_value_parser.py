from django_willpower.utils.parsing import WillpowerStringObject


def test_willpower_object():
    """
    WillpowerStringObject should correctly parse "Willpower object" syntax.
    """
    # Non string value is accepted but not parsed
    parsed = WillpowerStringObject(42)
    assert str(parsed.__repr__()) == "'42'"
    assert parsed == "42"
    assert type(parsed) is WillpowerStringObject
    assert parsed.implied_import is None
    assert parsed.parsed_object == 42
    assert parsed.is_wpower_syntax is False

    # String without prefix is not parsed
    parsed = WillpowerStringObject("settings.ARTICLE_PAGINATION")
    assert str(parsed.__repr__()) == (
        "'settings.ARTICLE_PAGINATION'"
    )
    assert str(parsed) == "settings.ARTICLE_PAGINATION"
    assert type(parsed) is WillpowerStringObject
    assert parsed.implied_import is None
    assert parsed.parsed_object == "settings.ARTICLE_PAGINATION"
    assert parsed.is_wpower_syntax is False

    # Proper string with prefix and with a simple import without module
    parsed = WillpowerStringObject("w-object://django.conf.settings/ARTICLE_PAGINATION")
    assert str(parsed.__repr__()) == (
        "'w-object://django.conf.settings/ARTICLE_PAGINATION'"
    )
    assert parsed.parsed_object == "django.conf.settings.ARTICLE_PAGINATION"
    assert type(parsed) is WillpowerStringObject
    assert parsed.implied_import == (None, "django.conf.settings")
    assert parsed.is_wpower_syntax is True

    # Proper string with prefix and with import with both name and module
    parsed = WillpowerStringObject("w-object://django.conf/settings/ARTICLE_PAGINATION")
    assert str(parsed.__repr__()) == (
        "'w-object://django.conf/settings/ARTICLE_PAGINATION'"
    )
    assert parsed.parsed_object == "settings.ARTICLE_PAGINATION"
    assert type(parsed) is WillpowerStringObject
    assert parsed.implied_import == ("django.conf", "settings")
    assert parsed.is_wpower_syntax is True
