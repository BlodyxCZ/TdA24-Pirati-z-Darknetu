from surrealdb import Surreal
from asyncio import get_event_loop
import os
import re

db = Surreal()

""" def check_db_connection() -> bool:
    loop = get_event_loop()
    try:
        if loop.run_until_complete(db.query("SELECT 1;"))[0]["result"] == 1:
            return True
        else:
            return False
    except:
        return False """

conn = None

def check_db_connection() -> bool:
    if conn == None:
        return False
    return conn.is_connected()

async def init() -> None:
    global conn

    try:
        with open("password.txt", "r") as file:
            password = file.read()
            if password == "":
                return
            print("Connecting to database...")
            conn = await db.connect("ws://" + os.environ.get("DATABASE_ADDRESS", "ondradoksy.com:8000") + "/rpc")
            await db.signin({"user": "root", "pass": password})
            await db.use("test", "test")
    except FileNotFoundError:
        return


async def get_lecturers() -> list:
    lecturers = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM lecturers;"))[0]["result"]
    
    for lecturer in lecturers:
        lecturer["tags"] = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM $tags", {
            "tags": lecturer["tags"]
        }))[0]["result"]

    return lecturers


async def get_lecturer(uuid) -> dict or None:
    lecturer = (await db.query('SELECT *, meta::id(id) AS uuid OMIT id FROM lecturers WHERE id = type::thing("lecturers", $uuid);', vars= {
        "uuid": uuid
    }))[0]["result"]
    
    if len(lecturer) == 0:
        return None
    
    lecturer = lecturer[0]

    lecturer["tags"] = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM $tags", {
        "tags": lecturer["tags"]
    }))[0]["result"]

    return lecturer


async def post_lecturer(data) -> dict:
    data["bio"] = re.sub(r"<(?!\/?(b|i|u|strong|em)(?=>|\s.*>))\/?.*?>", "", data["bio"]) # remove unallowed HTML tags
    
    if "tags" in data:
        tags = []
        for tag in data["tags"]:
            tags.append((await db.query("IF (SELECT * FROM tags WHERE name = $tag) = [] THEN SELECT VALUE id FROM (CREATE tags:uuid() SET name = $tag); ELSE SELECT VALUE id FROM tags WHERE name = $tag; END;", vars={
                "tag": tag["name"]
            }))[0]["result"][0])

        data["tags"] = tags
    else:
        data["tags"] = []
    
    lecturer = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id, tags FROM (CREATE lecturers:uuid() CONTENT $data);", vars={
        "data": data
    }))[0]["result"][0]

    lecturer["tags"] = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM $tags", vars={
        "tags": data["tags"]
    }))[0]["result"]
    
    return lecturer


async def put_lecturer(uuid, data) -> dict or None:
    if data == {}:
        return (await db.query('SELECT *, meta::id(id) AS uuid OMIT id FROM lecturers WHERE id = type::thing("lecturers", $uuid);', vars= {
            "uuid": uuid
        }))[0]["result"][0]

    lecturer = (await db.query('IF (SELECT * FROM type::thing("lecturers", $id)) = [] THEN RETURN null; ELSE UPDATE type::thing("lecturers", $id) MERGE $data; END;', vars={
        "id": uuid,
        "data": data
    }))[0]["result"]

    if lecturer == None:
        return None
    return lecturer[0]


async def delete_lecturer(uuid) -> bool:
    result = (await db.query('DELETE type::thing("lecturers", $uuid) RETURN BEFORE;', {
        "uuid": uuid
    }))[0]["result"]

    return result[0] != None


async def close() -> None:
    await db.close()


# <(?!\/?(b|i|u|strong|em)(?=>|\s.*>))\/?.*?>
