import os
from flask import Flask, jsonify
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Configure Azure Monitor with connection string from environment variable
configure_azure_monitor(connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"))

# Create Flask app
app = Flask(__name__)

# Auto-instrument inbound HTTP requests and outbound HTTP calls
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Health check endpoint
@app.route("/ok")
def ok():
    return jsonify({"status": "ok"})

# Home route
@app.route("/")
def home():
    return "Hello from Flask on Azure!"

# Endpoint to test exceptions
@app.route("/boom")
def boom():
    try:
        1 / 0
    except Exception as e:
        span = trace.get_current_span()
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        raise

# Another endpoint to test exceptions
@app.route("/error")
def error():
    return 1 / 0

# Another endpoint to intentionally cause error
@app.route("/cause-error")
def cause_error():
    return 1 / 0

if __name__ == "__main__":
    # Run Flask on port 8000 (Azure App Service Linux default)
    app.run(host="0.0.0.0", port=8000)
