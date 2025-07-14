import json


def validate_json(logger, path, clickapi=None):
    """
    Validate that given file path is a valid JSON file and returns it.

    Arguments:
        logger (logging.logger): The logger object to use to log errors.
        path (pathlib.Path): The file path.

    Keyword Arguments:
        clickapi (click): The Click module to use to abort program in case of error.

    Returns:
        object: Either an object from deserialized JSON if valid else return the
        value ``False``.
    """
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        logger.critical("Invalid JSON from: {}".format(path))
        logger.critical(str(e))

        if clickapi:
            raise clickapi.Abort()
        else:
            return False

    return payload


def validate_project_configuration(logger, basedir, custom_payload, clickapi=None,
                                   filename="cookiebaked.json"):
    """
    Validate project configuration.

    Either a custom config file has been given or the base directory must already have
    one. If one or the other, it must be a valid JSON file.

    Returns:
        object: Either an object from deserialized JSON if valid else return the
        value ``False``.
    """

    # Use custom config if given
    payload = (
        validate_json(logger, custom_payload, clickapi=clickapi)
        if custom_payload
        else False
    )

    # Else discover config file from base directory
    if not payload:
        baked_config = basedir / filename

        if not baked_config.exists() or not baked_config.is_file():
            msg = "Base directory is missing project configuration: {}".format(
                baked_config
            )
            logger.error(msg)

            if clickapi:
                raise clickapi.Abort()
            else:
                return False
        else:
            payload = json.loads(baked_config.read_text())

    return payload
