"""
Specific application exceptions.
"""


class DjangowillpowerBaseException(Exception):
    """
    Exception base.

    You should never use it directly except for test purpose. Instead make or
    use a dedicated exception related to the error context.
    """
    pass


class AppOperationError(DjangowillpowerBaseException):
    """
    Sample exception to raise from your code.
    """
    pass


class ProjectValidationError(DjangowillpowerBaseException):
    """
    Exception to raise from project configuration validation.
    """
    pass


class ModuleBuilderError(DjangowillpowerBaseException):
    """
    Exception to raise from module builder.
    """
    pass
