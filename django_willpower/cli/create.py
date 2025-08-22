import logging
from pathlib import Path

import click

import django_willpower
from ..core import ProjectRegistry, ProjectBuilder
from ..exceptions import ProjectBuildError, ProjectValidationError


@click.command()
@click.argument(
    "basedir",
    nargs=1,
    required=True,
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    metavar="<basedir>",
)
@click.argument(
    "config",
    nargs=1,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    metavar="<config>",
)
@click.pass_context
def create_command(context, basedir, config):
    """
    Willpower command to build a project.

    'basedir' argument is the base directory path where it will create the project
    directory with its application structure and modules. It means for a given base
    directory '/foo/bar' for a project named "ping", this will create '/foo/bar/ping/'.

    'config' is a path to a valid JSON file which contain the full project
    configuration. See documentation to know the structure of this JSON in details.
    """
    logger = logging.getLogger(django_willpower.__pkgname__)

    # Display some useful informations from options
    logger.info("🚀 Starting")
    logger.debug("🔧 Base directory: {}".format(basedir.resolve()))

    project = ProjectRegistry()

    try:
        project.load_configuration(config)
    except ProjectValidationError as e:
        logger.critical(str(e))
        raise click.Abort()

    # Run builder processor
    try:
        builder = ProjectBuilder(project, basedir)
        builder.process()
    except ProjectBuildError as e:
        logger.critical(str(e))
        raise click.Abort()

    logger.info("Finished")
