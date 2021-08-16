from flask import Flask

from hoststats.server import metrics_api

app = Flask(__name__)
app.register_blueprint(metrics_api)
