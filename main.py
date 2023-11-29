from flask import Flask, render_template
import atexit
import db as db
import asyncio
import sass
import os

# SCSS

sass.compile(dirname=('static/scss', 'static/css'), output_style='compressed')


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

@app.route("/lecturers", methods=["GET"])
async def get_lecturers():
    return await db.get_lecturers(), 200

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

async def main():
    print("Starting server...")
    atexit.register(exit_handler)
    print("Connecting to database...")
    try:
        await db.init()
    except:
        print("Failed to connect to database! Continuing anyway...")
    print("Starting webserver...")
    app.run(port=80, host="0.0.0.0")

if __name__ == "__main__":
   asyncio.run(main())