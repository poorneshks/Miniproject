from flask import Flask
app = Flask(__name__)

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

