import datetime
import json
import types
from pathlib import Path


class ExtendedJsonEncoder(json.JSONEncoder):
    """
    Additional opiniated support for more basic object types.

    Usage sample: ::

        json.dumps(..., cls=ExtendedJsonEncoder)
    """
    def default(self, obj):
        # Convert bytes to unicode string
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        # Convert pathlib.Path to a string
        if isinstance(obj, Path):
            return str(obj)
        # Convert set to a list
        if isinstance(obj, set):
            return list(obj)
        # Convert dates/times in ISO format string
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        # Convert callable to its name as a string
        if callable(obj):
            return obj.__name__
        # Convert generator to its name as a string
        if isinstance(obj, types.GeneratorType):
            return obj.__name__

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
