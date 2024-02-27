from quart import Quart, render_template, request
from quart_auth import QuartAuth, basic_auth_required
import atexit
import db as db
import sass
import logging
import sys
from schemas import *
import os
import signal
import utils.email, utils.icalendar

def signal_handler(sig, frame):
    print('Shutting down...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

os.chdir(os.path.dirname(os.path.realpath(__file__)))

app = Quart(__name__)

# Logging

logging.basicConfig(filename="logs.log", level=logging.DEBUG)
QuartAuth(app)

@app.before_request
async def log_request():
    # Totally not a security risk nuh uh :3
    logging.info(f"Request: {request.method} {request.path} from {request.remote_addr} with data {request.headers}; {await request.get_data()}; {await request.get_json()}")

# SCSS

sass.compile(dirname=('static/scss', 'static/css'), output_style='compressed')

# CSS

@app.route("/css/<file>.css")
async def css(file):
    return await app.send_static_file("css/" + file + ".css")

# JS

@app.route("/js/<file>.js")
async def js(file):
    return await app.send_static_file("js/" + file +".js")

# Pages

@app.route("/")
async def index():
    return await render_template("index.html")


@app.route("/dev")
async def dev():
    return await render_template("dev.html")

@app.route("/log")
async def log_page():
    return await render_template("log.html")


@app.route("/lecturer")
async def lecturer():
    return await render_template("lecturer.html")


@app.route("/auth")
async def update_password():
    return await render_template("auth.html")


@app.route("/lecturer/<uuid>", methods=["GET"])
async def lecturer_page(uuid):
    lecturer = await db.get_lecturer(uuid)
    if lecturer is None:
        return await render_template("404.html"), 404
    if lecturer["title_after"] != "" and lecturer["title_after"] != None:
        lecturer["last_name"] += ","
    if lecturer["middle_name"] == None:
        lecturer["middle_name"] = ""
    if lecturer["title_before"] == None:
        lecturer["title_before"] = ""
    if lecturer["title_after"] == None:
        lecturer["title_after"] = ""
    print(lecturer)
    return await render_template("lecturer_template.html", lecturer=lecturer)


@app.route("/lecturer/<uuid>/reservations", methods=["GET"])
async def lecturer_reservations(uuid):
    lecturer = await db.get_lecturer(uuid)
    if lecturer is None:
        return await render_template("404.html"), 404
    return await render_template("reservations.html", lecturer=lecturer)


@app.errorhandler(404)
async def page_not_found(e):
    return await render_template("404.html"), 404

# API

""" @app.route("/api")
def api():
    # Portal reference
    return {"secret": "The cake is a lie"}, 200 """

@app.route("/api/locations", methods=["GET"])
async def get_locations():
    locations = await db.get_all_locations()
    return locations, 200


@app.route("/api/login", methods=["POST"])
async def login():
    data = await request.get_json()

    response = await db.login(data)
    return response, 200


@app.route("/api/tags", methods=["GET"])
async def get_tags():
    tags = await db.get_all_tags()
    return tags, 200


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
@basic_auth_required()
async def post_lecturer():
    data = await request.get_json()
    if not validate_post_lecturer(data):
        return {"code": 400, "message": "Invalid request body"}, 400

    response = await db.post_lecturer(data)
    return response, 201


@app.route("/api/lecturers/<uuid>", methods=["PUT"])
@basic_auth_required()
async def put_lecturer(uuid):
    lecturer = await db.put_lecturer(uuid, await request.get_json())
    if lecturer == None:
        return {"code": 404, "message": "User not found"}, 404
    return lecturer, 200


@app.route("/api/lecturers/<uuid>", methods=["DELETE"])
@basic_auth_required()
async def delete_lecturer(uuid):
    success = await db.delete_lecturer(uuid)
    if success:
        return {"code": 204, "message": "User deleted"}, 204
    return {"code": 404, "message": "User not found"}, 404


@app.route("/api/reservations/<uuid>", methods=["GET"])
async def get_reservations(uuid):
    # Returns full reservation data if token is the lecturer's (token is taken from the Bearer token)
    token = request.headers.get("Authorization")

    if token != None:
        token = token.split(" ")[1]

        lecturer_uuid = await db.get_lecturer_uuid_from_token(token)

        if lecturer_uuid is None:
            return {"code": 401, "message": "Invalid token"}, 401
        
        if lecturer_uuid == uuid:
            reservations = await db.get_reservations(uuid, True)
    else:
        reservations = await db.get_reservations(uuid, False)

    if reservations is None:
        return {"code": 404, "message": "Lecturer not found"}, 404
    return reservations, 200


@app.route("/api/reservations/<uuid>/icalendar", methods=["GET"])
async def get_reservations_icalendar(uuid):
    token = request.headers.get("Authorization")
    if token != None:
        token = token.split(" ")[1]

        lecturer_uuid = await db.get_lecturer_uuid_from_token(token)

        if lecturer_uuid is None:
            return {"code": 401, "message": "Invalid token"}, 401
        
        if lecturer_uuid == uuid:
            reservations = await db.get_reservations(uuid, True)

        return utils.icalendar.generate_icalendar(reservations), 200
    else:
        return {"code": 401, "message": "Invalid token"}, 401


@app.route("/api/reservations/<uuid>", methods=["POST"])
async def post_reservation(uuid):
    data = await request.get_json()

    # TODO: Check if date is available

    data["uuid"] = uuid

    response = await db.post_reservation(data)

    try:
        utils.email.send_new_reservation_email(data["student_email"])
    except:
        pass

    return response, 201


@app.route("/api/reservations/confirm", methods=["PUT"])
@basic_auth_required()
async def confirm_reservation():
    data = await request.get_json()

    lecturer_uuid = await db.get_lecturer_uuid_from_token(data["token"])

    if lecturer_uuid is None:
        return {"code": 401, "message": "Invalid token"}, 401

    reservation = await db.confirm_reservation(lecturer_uuid, data["reservation"])

    if reservation:
        return {"code": 200, "message": "Reservation confirmed"}, 200
    return {"code": 404, "message": "Reservation not found"}, 404


@app.route("/api/reservations/", methods=["DELETE"])
@basic_auth_required()
async def delete_reservation():
    data = await request.get_json()

    lecturer_uuid = await db.get_lecturer_uuid_from_token(data["token"])

    if lecturer_uuid is None:
        return {"code": 401, "message": "Invalid token"}, 401

    reservation = await db.delete_reservation(lecturer_uuid, data["reservation"])

    if reservation:
        return {"code": 200, "message": "Reservation deleted"}, 200
    return {"code": 404, "message": "Reservation not found"}, 404


# Server utilities

""" @app.before_request
async def check_db_connection_before_request():
    if not db.check_db_connection():
        await db.init() """


@app.route("/api/conn")
async def check_db_connection():
    await db.init()
    return {"msg": "Tried to renew connection."}, 200


@app.route("/api/log")
async def log():
    with open("logs.log", "r") as file:
        return file.read(), 200


@app.route("/api/dbpasswd", methods=["POST"])
async def post_update_dbpassword():
    with open("password.txt", "w+") as file:
        file.write((await request.form)["password"])

    await db.init()
    return "Updated database password", 200


@app.route("/api/emailpasswd", methods=["POST"])
async def post_update_emailpassword():
    with open("email_password.txt", "w+") as file:
        file.write((await request.form)["password"])

    utils.email.update_password()
    return "Updated email password", 200


@app.route("/api/basicauth", methods=["POST"])
async def post_update_basicauth():
    app.config["QUART_AUTH_BASIC_USERNAME"] = (await request.form)["username"]
    app.config["QUART_AUTH_BASIC_PASSWORD"] = (await request.form)["password"]    
    return "Basic Auth updated", 200


async def exit_handler() -> None:
    print("Closing database connection...")
    await db.close()
    os.exit(0)


def main() -> None:
    # Clear logs
    with open("logs.log", "w+") as file:
        file.write("")
    
    # Set default values
    app.config["QUART_AUTH_BASIC_USERNAME"] = ""
    app.config["QUART_AUTH_BASIC_PASSWORD"] = ""
    
    print("Starting server...")
    atexit.register(exit_handler)
    print("Connecting to database...")
    """ try:
        db.init()
    except:
        print("Failed to connect to database! Continuing anyway...") """
    print("Starting webserver...")
    app.run(port=80, host="0.0.0.0")


if __name__ == "__main__":
    main()
