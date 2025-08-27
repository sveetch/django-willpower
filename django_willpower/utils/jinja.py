
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


def str_format(value, *args, **kwargs):
    """
    Filter to perform a string formatting operation.

    This is not to be confused with builtin Jinja filter named ``format`` which perform
    the printf-style formatting.

    Samples: ::
        {{ "{}bar"|format_operation("foo") }}
        {{ "{foo}bar"|format_operation(foo="foo") }}

    Arguments:
        value (string): A string value where to perform formatting operation.
        *args: Arguments passed to the ``String.format()`` method.
        **kwargs: Keyword arguments passed to the ``String.format()`` method.

    Returns:
        (string): Formatted string.
    """
    return value.format(*args, **kwargs)
