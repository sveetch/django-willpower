
def split_stack_path(path):
    """
    Split a stack path into parts.

    Returns:
        tuple: Respectively the application part, the component part and the
            module part. Either as string or null in some case because the
            application and modules are optional.
    """
    app = None
    component = None
    module = None

    if len(path.split("@")) > 1:
        app, bases = path.split("@")
    else:
        bases = path

    if len(bases.split(":")) > 1:
        component, module = bases.split(":")
    else:
        component = bases

    return app, component, module
