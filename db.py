from surrealdb import Surreal
from main import loop
import os
import re

db = Surreal()


async def init() -> None:
    await db.connect("http://" + os.environ["DATABASE_ADDRESS"] + "/rpc")
    await db.signin({"user": "root", "pass": "root"})
    await db.use("test", "test")


def get_lecturers() -> list:
    lecturers = loop.run_until_complete(db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM lecturers;"))[0]["result"]
    
    for lecturer in lecturers:
        lecturer["tags"] = loop.run_until_complete(db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM $tags", {
            "tags": lecturer["tags"]
        }))[0]["result"]

    return lecturers


def get_lecturer(uuid) -> dict or None:
    lecturer = loop.run_until_complete(db.query('SELECT *, meta::id(id) AS uuid OMIT id FROM lecturers WHERE id = type::thing("lecturers", $uuid);', vars= {
        "uuid": uuid
    }))[0]["result"]
    
    if len(lecturer) == 0:
        return None
    
    lecturer = lecturer[0]

    lecturer["tags"] = loop.run_until_complete(db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM $tags", {
        "tags": lecturer["tags"]
    }))[0]["result"]

    return lecturer


def post_lecturer(data) -> dict:
    data["bio"] = re.sub(r"<(?!\/?(b|i|u|strong|em)(?=>|\s.*>))\/?.*?>", "", data["bio"]) # remove unallowed HTML tags
    
    if "tags" in data:
        tags = []
        for tag in data["tags"]:
            tags.append(loop.run_until_complete(db.query("IF (SELECT * FROM tags WHERE name = $tag) = [] THEN SELECT VALUE id FROM (CREATE tags:uuid() SET name = $tag); ELSE SELECT VALUE id FROM tags WHERE name = $tag; END;", vars={
                "tag": tag["name"]
            }))[0]["result"][0])

        data["tags"] = tags
    else:
        data["tags"] = []
    
    lecturer = loop.run_until_complete(db.query("SELECT *, meta::id(id) AS uuid OMIT id, tags FROM (CREATE lecturers:uuid() CONTENT $data);", vars={
        "data": data
    }))[0]["result"][0]

    lecturer["tags"] = loop.run_until_complete(db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM $tags", {
        "tags": data["tags"]
    }))[0]["result"]
    
    return lecturer


def delete_lecturer(uuid) -> bool:
    result = loop.run_until_complete(db.query('DELETE type::thing("lecturers", $uuid) RETURN BEFORE;', {
        "uuid": uuid
    }))[0]["result"]

    return result[0] != None


async def close() -> None:
    await db.close()


# <(?!\/?(b|i|u|strong|em)(?=>|\s.*>))\/?.*?>
