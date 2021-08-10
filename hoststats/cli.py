import click

import hoststats


@click.group()
def top():
    pass


@top.command()
def start():
    click.echo("Starting hoststats")


@top.command()
def stop():
    click.echo("Stopping hoststats")


def main():
    top()
