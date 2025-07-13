import click

from django_willpower import __version__


@click.command()
@click.pass_context
def version_command(context):
    """
    Print out version information.
    """
    click.echo("django-willpower {}".format(__version__))
