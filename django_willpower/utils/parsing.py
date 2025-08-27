from collections import UserString


class WillpowerStringObject(UserString):
    """
    Encapsulated text value which support Willpower object syntax.

    This object is a subclass of UserString and so will behavior like a string with
    additional feature for the syntax.

    The "Willpower object" syntax is: ::

        w-object://[[MODULE/]NAME/OBJECT]

    Parsing is only done with a string starting with the syntax prefix ``w-object://``.

    ``MODULE`` and ``NAME`` are optional, ``OBJECT`` is required. Object is always
    in the returned string representation, if there is an imported name it will
    prefix the object. Module is only reported from ``implied_import`` attribute
    with the imported name.

    Finally the parsing results are reachable from attributes ``parsed_object`` and
    ``implied_import``.

    As an example: ::
        >>> foo = WillpowerStringObject("Foo")
        >>> foo
        Foo
        >>> foo.implied_import
        None
        >>> foo.parsed_object
        Foo

        >>> bar = WillpowerStringObject("w-object://ping/pong/bar")
        w-object://ping/pong/bar
        >>> bar.implied_import
        ("ping", "pong")
        >>> bar.parsed_object
        pong.bar

        >>> zip = WillpowerStringObject("w-object://pong/zip")
        w-object://pong/zip
        >>> zip.implied_import
        (None, "pong")
        >>> zip.parsed_object
        pong.zip


    Attributes:
        implied_import (tuple): First item will be the module name part if given else
            it will be None. Second item is the name part.
        parsed_object (string): Resolved object with import name as prefix.
    """
    PREFIX_MARK = "w-object://"

    def __init__(self, value):
        self.implied_import = None
        self.parsed_object = self.parse_object(value)
        super().__init__(value)

    def parse_object(self, value):
        """
        Parse elligible string to find possible import parts and object part from
        syntax.

        If implied import is found it will be set on instance attribute
        ``implied_import``.

        Returns:
            string: Found object part from syntax.
        """
        if isinstance(value, str) and value.startswith(self.PREFIX_MARK):
            # Remove prefix
            content = value[len(self.PREFIX_MARK):].split("/")

            # Add module part as None if there was none from value
            if len(content[:-1]) == 1:
                self.implied_import = tuple([None] + content[:-1])
            # Get both module and name
            elif len(content[:-1]) == 2:
                self.implied_import = tuple(content[:-1])
            # Invalid syntax we only allow for two parts (module and name) before the
            # the object part
            else:
                msg = "Too much items in path: {}"
                raise NotImplementedError(msg.format(content[:-1]))

            return (
                content[-1]
                if not self.implied_import
                else self.implied_import[1] + "." + content[-1]
            )

        # Non elligible values to parsing are just returned unchanged
        return value
