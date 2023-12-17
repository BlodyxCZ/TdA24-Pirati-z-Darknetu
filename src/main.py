from quart import Quart, render_template, request
import atexit
import db as db
import sass
import logging
import sys
from schemas import *
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

app = Quart(__name__)

# SCSS

sass.compile(dirname=('static/scss', 'static/css'), output_style='compressed')

# CSS


@app.route("/css/styles.css")
async def css():
    return await app.send_static_file("css/styles.css")

# JS

@app.route("/js/<file>.js")
async def js(file):
    return await app.send_static_file("js/" + file +".js")

# Pages


@app.route("/")
async def index():
    return await render_template("index.html")

@app.route("/log")
async def log_page():
    return await render_template("log.html")

@app.route("/lecturer")
async def lecturer():
    return await render_template("lecturer.html")


@app.route("/dbpasswd")
async def update_password():
    return await render_template("dbpasswd.html")

# API


""" @app.route("/api")
def api():
    # Portal reference
    return {"secret": "The cake is a lie"}, 200 """


@app.route("/api/lecturers", methods=["GET"])
async def get_lecturers():
    lecturers = await db.get_lecturers()
    return lecturers, 200


@app.route("/api/lecturers/<uuid>", methods=["GET"])
async def get_lecturer(uuid):
    lecturer = await db.get_lecturer(uuid)
    if lecturer is None:
        return {"code": 404, "message": "User not found"}, 404
    return lecturer, 200


@app.route("/api/lecturers", methods=["POST"])
async def post_lecturer():
    data = await request.get_json()
    #if not validate_post_lecturer(data):
    #    return {"code": 400, "message": "Invalid request body"}, 400

    response = await db.post_lecturer(data)
    return response, 201


@app.route("/api/lecturers/<uuid>", methods=["PUT"])
async def put_lecturer(uuid):
    lecturer = await db.put_lecturer(uuid, await request.get_json())
    if lecturer == None:
        return {"code": 404, "message": "User not found"}, 404
    return lecturer, 200


@app.route("/api/lecturers/<uuid>", methods=["DELETE"])
async def delete_lecturer(uuid):
    success = await db.delete_lecturer(uuid)
    if success:
        return {"code": 204, "message": "User deleted"}, 204
    return {"code": 404, "message": "User not found"}, 404

# Server utilities


@app.before_request
async def check_db_connection_before_request():
    if not db.check_db_connection():
        await db.init()


@app.route("/api/conn")
async def check_db_connection():
    await db.init()
    return {"msg": "Tried to renew connection."}, 200


@app.route("/api/log")
async def log():
    with open("logs.log", "r") as file:
        return file.read(), 200


@app.route("/api/dbpasswd", methods=["POST"])
async def post_update_password():
    with open("password.txt", "w+") as file:
        file.write((await request.form)["password"])
        return "Updated database password", 200


async def exit_handler() -> None:
    print("Closing database connection...")
    await db.close()
    os.exit(0)


def main() -> None:
    # Clear logs
    with open("logs.log", "w+") as file:
        file.write("")
    
    logging.basicConfig(filename="logs.log", filemode="w", format="[%(levelname)s] : %(message)s")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    print("Starting server...")
    atexit.register(exit_handler)
    print("Connecting to database...")
    try:
        pass #db.init()
    except:
        print("Failed to connect to database! Continuing anyway...")
    print("Starting webserver...")
    app.run(port=80, host="0.0.0.0")


if __name__ == "__main__":
    main()
