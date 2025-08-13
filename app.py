from flask import Flask
app = Flask(__name__)

import os
from flask import Flask, jsonify
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Send telemetry to App Insights using your connection string
configure_azure_monitor(connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"))

app = Flask(__name__)

# Auto-instrument inbound HTTP requests and outbound calls
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/ok")
def ok():
    return jsonify({"status": "ok"})

# An endpoint that throws (to test correlation)
@app.route("/boom")
def boom():
    try:
        1 / 0
    except Exception as e:
        # Attach exception to the current request span (extra safety)
        span = trace.get_current_span()
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        raise  # also let Flask raise it so it’s captured automatically


@app.route("/")
def home():
    return "Hello from Flask on Azure!"

@app.route("/error")
def error():
    # intentional error to test monitoring/alerts
    return 1 / 0

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

@app.route('/cause-error')
def cause_error():
    # This will cause a ZeroDivisionError intentionally
    return 1 / 0

