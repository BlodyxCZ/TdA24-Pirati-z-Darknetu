from flask import Flask, render_template, request
import atexit
import db as db
import asyncio
import sass

# SCSS

sass.compile(dirname=('static/scss', 'static/css'), output_style='compressed')

loop = asyncio.get_event_loop()
app = Flask(__name__)

# CSS

@app.route("/css/styles.css")
def css():
    return app.send_static_file("css/styles.css")

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

@app.route("/api/lecturers", methods=["GET"])
def get_lecturers():
    lecturers = db.get_lecturers()
    return lecturers, 200

@app.route("/api/lecturers/<uuid>", methods=["GET"])
def get_lecturer(uuid):
    lecturer = db.get_lecturer(uuid)
    if lecturer is None:
        return {"code": 404, "message": "User not found"}, 404
    return lecturer, 200

@app.route("/api/lecturers", methods=["POST"])
def post_lecturer():
    response = db.post_lecturer(request.get_json())
    return response, 201

@app.route("/api/lecturers/<uuid>", methods=["PUT"])
def put_lecturer(uuid):
    return "WIP", 404

@app.route("/api/lecturers/<uuid>", methods=["DELETE"])
def delete_lecturer(uuid):
    success = db.delete_lecturer(uuid)
    if success:
        return {"code": 204, "message": "User deleted"}, 204
    return {"code": 404, "message": "User not found"}, 404

# Server utilities

def exit_handler() -> None:
    print("Closing database connection...")
    loop.run_until_complete(db.close())

def main() -> None:
    print("Starting server...")
    atexit.register(exit_handler)
    print("Connecting to database...")
    try:
        loop.run_until_complete(db.init())
    except:
        print("Failed to connect to database! Continuing anyway...")
    print("Starting webserver...")
    app.run(port=80, host="0.0.0.0")

if __name__ == "__main__":
   main()