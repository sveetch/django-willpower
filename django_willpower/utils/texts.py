import string
import unicodedata


def normalize_text(value):
    """
    Common way to normalize a text to a alphanumeric version without any special
    characters.

    In short this would transform : ::

        Élà-plôp, lorem_ipsum.

    To: ::
        Ela plop lorem ipsum

    Arguments:
        value (string): Text to normalize.

    Returns:
        string: Normalized text.
    """
    # Replace all unicode character with its 'normalized' one and then replace every
    # punctuation character by a single whitespace
    cleaned = "".join([
        " " if v in string.punctuation else v
        for v in (
            unicodedata.normalize("NFKD", value).encode(
                "ascii",
                "ignore"
            ).decode("ascii")
        ).replace(",", "")
    ])
    # Finally ensure there are no useless whitespaces
    return " ".join(cleaned.split())


def text_to_pascal_case(value):
    """
    Normalize value to *Pascal case* that is suitable for a Python class name.

    .. Todo::
        This is a naive implementation that may need improvement.
    """
    cleaned = value.replace("(", "").replace(")", "")
    return normalize_text(cleaned).title().replace(" ", "")


def text_to_snake_case(value):
    """
    Normalize value to *Snake case* that is suitable for a Python module name (or a
    variable).

    .. Todo::
        This is a naive implementation that may need improvement.
    """
    cleaned = value.replace("(", "").replace(")", "")
    return normalize_text(cleaned).lower().replace(" ", "_")
