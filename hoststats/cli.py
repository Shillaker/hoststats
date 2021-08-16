import click

from hoststats.app import app


@click.group()
def top():
    pass


@top.command()
def start():
    click.echo("Starting hoststats")
    app.run()


def main():
    top()
