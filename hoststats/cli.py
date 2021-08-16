import click

from hoststats.app import app


@click.group()
def top():
    pass


@top.command()
def start():
    click.echo("Starting hoststats")
    app.run(debug=True, host="0.0.0.0")


def main():
    top()
