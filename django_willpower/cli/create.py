"""
Main entrance to commandline actions

DEPRECATED: In favor of the new 'new_create' command that use the new Appstack, registry and builder.

.. Todo::
    Old usage sample: ::
        .venv/bin/willpower -v 5 dist/drant-proto-1/ -d data/drant_declarations.json --no-structure
"""
import json
import logging
from pathlib import Path

import click
from cookiecutter.main import cookiecutter

import django_willpower
from ..logger import init_logger
from ..builder import AppBuilder
from ..exceptions import ModuleBuilderError
from ..utils.validations import validate_json, validate_project_configuration


@click.command()
@click.argument(
    "basedir",
    required=True,
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    metavar="<basedir>",
)
@click.option(
    "-d",
    "--declarations",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    metavar="<path>",
    help=(
        "Path to a JSON file for models declarations. If not given a default one from "
        "package will be used, this will result to a basic Blog application."
    ),
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    metavar="<path>",
    help=(
        "Path to a JSON file for application configuration. Default command behavior "
        "is to try to find the configuration from the structure in base directory "
        "but this option allows to use a custom configuration instead."
    ),
)
@click.option(
    "--no-structure",
    is_flag=True,
    help=(
        "Disable creation of project structure. If this option is used the option "
        "'--config' must be given with a proper JSON configuration. Default behavior "
        "when this option is not given is to involve cookiecutter to create the base "
        "project structure."
    ),
)
@click.option(
    "--cookie-replay",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    metavar="<path>",
    help=(
        "Path to a JSON file for the cookiecutter replay that avoid to be prompted "
        "for project parameters if cookiecutter is involved."
    ),
)
@click.pass_context
def create_command(context, basedir, declarations, config, no_structure, cookie_replay):
    """
    Willpower command to build an application structure from models declarations.

    'basedir' argument is the base directory path where it will create the project
    directory with its application structure and modules. It means for a given base
    directory '/foo/bar' for a project named "ping", this will create '/foo/bar/ping/'.

    Creation of base project structure will be done with Cookiecutter that will prompt
    you for some parameters if not explicitely disabled with option '--no-structure'
    then so the base directory must already exists.
    """
    logger = logging.getLogger(django_willpower.__pkgname__)

    willpower_basepath = Path(django_willpower.__file__).parent

    # WARNING: Temporary use sample declarations file if not given, the default should
    # be a better sample
    declarations = (
        declarations
        if declarations
        else willpower_basepath / "data/sample_declarations.json"
    )

    # Display some useful informations from options
    logger.info("🚀 Starting")
    logger.debug("🔧 Base directory: {}".format(basedir.resolve()))
    logger.debug("🔧 Declarations file: {}".format(declarations.resolve()))
    if cookie_replay:
        logger.debug("🔧 Cookiecutter replay: {}".format(cookie_replay.resolve()))

    # Valide and deserialize payloads
    declarations_payload = validate_json(logger, declarations, clickapi=click)
    replay_payload = (
        validate_json(logger, cookie_replay, clickapi=click)
        if cookie_replay
        else None
    )

    # Create project structure with cookiecutter if not disabled
    if not no_structure:
        logger.info("🏗️Creating base project structure")
        projectdir = Path(cookiecutter(
            str(willpower_basepath / "structure_template"),
            output_dir=str(basedir),
            replay=replay_payload,
        ))

        # Do not blindly assert that returned path is correct
        if not projectdir.exists():
            msg = "Something went wrong during creation on path: {}"
            logger.critical(msg.format(projectdir))
            raise click.Abort()

        logger.debug("🔧 Project created: {}".format(projectdir))
    # If cookiecutter is not involved to create project, the base directory must
    # already exists.
    # NOTE: Maybe create it automatically to avoid behavior difference with
    # cookiecutter ?
    else:
        if not basedir.exists():
            logger.critical("Given base directory does not exist")
            raise click.Abort()
        else:
            # We currently endorse the basedir as the project dir despite it is
            # a behavior change with cookiecutter that have project dir inside basedir
            projectdir = basedir

    # Now we can discover the project configuration either from project structure or
    # custom one from command option
    config_payload = validate_project_configuration(
        logger,
        projectdir,
        config,
        clickapi=click
    )

    # Finally process builder
    logger.info("🏗️Creating application modules")
    try:
        builder = AppBuilder(logger, config_payload, projectdir, declarations_payload)
        builder.process()
    except ModuleBuilderError as e:
        logger.critical(str(e))
        raise click.Abort()

    logger.info("Finished")