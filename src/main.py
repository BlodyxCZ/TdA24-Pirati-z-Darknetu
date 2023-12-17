from flask import Flask, render_template, request
import atexit
import db as db
import asyncio
import sass
import logging
import sys
from flask_expects_json import expects_json
from schemas import *
import nest_asyncio
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

nest_asyncio.apply()
app = Flask(__name__)

# SCSS

sass.compile(dirname=('static/scss', 'static/css'), output_style='compressed')

# CSS


@app.route("/css/styles.css")
def css():
    return app.send_static_file("css/styles.css")

# JS

@app.route("/js/<file>.js")
def js(file):
    return app.send_static_file("js/" + file +".js")

# Pages


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/log")
def log_page():
    return render_template("log.html")

@app.route("/lecturer")
def lecturer():
    return render_template("lecturer.html")


@app.route("/dbpasswd")
def update_password():
    return render_template("dbpasswd.html")

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
@expects_json(lecturer_post_schema)
def post_lecturer():
    response = db.post_lecturer(request.get_json())
    return response, 201


@app.route("/api/lecturers/<uuid>", methods=["PUT"])
def put_lecturer(uuid):
    lecturer = db.put_lecturer(uuid, request.get_json())
    if lecturer == None:
        return {"code": 404, "message": "User not found"}, 404
    return lecturer, 200


@app.route("/api/lecturers/<uuid>", methods=["DELETE"])
def delete_lecturer(uuid):
    success = db.delete_lecturer(uuid)
    if success:
        return {"code": 204, "message": "User deleted"}, 204
    return {"code": 404, "message": "User not found"}, 404

# Server utilities


@app.before_request
def check_db_connection_before_request():
    if not db.check_db_connection():
        db.init()
    # asyncio.run(db.init())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(db.init())


@app.route("/api/conn")
def check_db_connection():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db.init())
    return {"msg": "Tried to renew connection."}, 200


@app.route("/api/log")
def log():
    with open("logs.log", "r") as file:
        return file.read(), 200


@app.route("/api/dbpasswd", methods=["POST"])
def post_update_password():
    with open("password.txt", "w+") as file:
        file.write(request.form["password"])
        return "Updated database password", 200


def exit_handler() -> None:
    loop = asyncio.get_event_loop()
    print("Closing database connection...")
    loop.run_until_complete(db.close())
    os.exit(0)


def main() -> None:
    # Clear logs
    with open("logs.log", "w+") as file:
        file.write("")
    
    loop = asyncio.get_event_loop()
    logging.basicConfig(filename="logs.log", filemode="w", format="[%(levelname)s] : %(message)s")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
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
