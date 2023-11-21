from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lecturer")
def lecturer():
    return render_template("lecturer.html")

@app.route("/api")
def api():
    # Portal reference
    return {"secret": "The cake is a lie"}, 200

if __name__ == "__main__":
    app.run(port=80, host="0.0.0.0")