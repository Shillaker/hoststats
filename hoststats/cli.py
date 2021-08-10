import click
from flask import Flask

from hoststats.server.server import metrics_api

app = Flask(__name__)
app.register_blueprint(metrics_api)


@click.group()
def top():
    pass


@top.command()
def start():
    click.echo("Starting hoststats")
    app.run()


def main():
    top()
