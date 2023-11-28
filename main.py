from flask import Flask, render_template
import atexit
import db as db

app = Flask(__name__)

# Pages

""" @app.route("/")
def index():
    return render_template("index.html") """

@app.route("/lecturer")
def lecturer():
    return render_template("lecturer.html")

# API

""" @app.route("/api")
def api():
    # Portal reference
    return {"secret": "The cake is a lie"}, 200 """

@app.route("/lecturers", methods=["GET"])
def get_lecturers():
    return "WIP", 404

@app.route("/lecturers/<int:uuid>", methods=["GET"])
def get_lecturer(uuid):
    return "WIP", 404

@app.route("/lecturers", methods=["POST"])
def post_lecturer():
    return "WIP", 404

@app.route("/lecturers/<int:uuid>", methods=["PUT"])
def put_lecturer(uuid):
    return "WIP", 404

@app.route("/lecturers/<int:uuid>", methods=["DELETE"])
def delete_lecturer(uuid):
    return "WIP", 404

# Server utilities

def exit_handler():
    print("Closing database connection...")
    db.close()

if __name__ == "__main__":
    atexit.register(exit_handler)
    db.init()
    app.run(port=80, host="0.0.0.0")