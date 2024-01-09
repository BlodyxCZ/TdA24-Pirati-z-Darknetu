from surrealdb import Surreal, ws
import os
import re

db = Surreal()

async def check_db_connection() -> None:
    try:
        if (await db.query("RETURN true;"))[0]["result"] != True:
            await init()
    except:
        await init()

async def init() -> None:
    try:
        with open("password.txt", "r") as file:
            password = file.read()
            if password == "":
                return
            print("Connecting to database...")
            await db.connect("http://" + os.environ.get("DATABASE_ADDRESS", "130.61.210.43:8000") + "/rpc")
            await db.signin({"user": "root", "pass": password})
            await db.use("tda", "tda")
    except FileNotFoundError:
        return


async def get_lecturers() -> list:
    await check_db_connection()
    lecturers = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM lecturers;"))[0]["result"]
    
    for lecturer in lecturers:
        lecturer["tags"] = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM $tags", {
            "tags": lecturer["tags"]
        }))[0]["result"]

    return lecturers


async def get_lecturer(uuid) -> dict or None:
    await check_db_connection()
    lecturer = (await db.query('SELECT *, meta::id(id) AS uuid OMIT id FROM lecturers WHERE id = type::thing("lecturers", $uuid);', vars= {
        "uuid": uuid
    }))[0]["result"]
    
    if len(lecturer) == 0:
        return None
    
    lecturer = lecturer[0]

    lecturer["tags"] = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM $tags;", {
        "tags": lecturer["tags"]
    }))[0]["result"]

    return lecturer

async def get_tags(tag_ids: list) -> list:
    await check_db_connection()
    tags = []
    for tag in tag_ids:
        tags.append((await db.query('SELECT *, meta::id(id) AS uuid OMIT id FROM type::thing($tag_id);', {
            "tag_id": tag
        }))[0]["result"][0])

    return tags

async def post_lecturer(data) -> dict:
    await check_db_connection()
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
    await check_db_connection()
    if data == {}:
        return (await db.query('SELECT *, meta::id(id) AS uuid OMIT id FROM lecturers WHERE id = type::thing("lecturers", $uuid);', vars= {
            "uuid": uuid
        }))[0]["result"][0]

    if "tags" in data:
        tags = []
        for tag in data["tags"]:
            tags.append((await db.query("LET $tag = (SELECT * FROM tags WHERE name = $data.name); IF array::len($tag) != 0 THEN RETURN $tag.id; ELSE RETURN (CREATE tags:uuid() SET name = $data.name).id; END;", vars= {
                "data": tag
            }))[1]["result"][0])

        data["tags"] = tags

    lecturer = (await db.query('IF (SELECT * FROM type::thing("lecturers", $id)) = [] THEN RETURN null; ELSE SELECT *, meta::id(id) AS uuid OMIT id FROM (UPDATE type::thing("lecturers", $id) MERGE $data); END;', vars={
        "id": uuid,
        "data": data
    }))[0]["result"]

    if lecturer == None:
        return None
    lecturer = lecturer[0]
    
    if "tags" in lecturer:
        lecturer["tags"] = await get_tags(lecturer["tags"])

    return lecturer


async def delete_lecturer(uuid) -> bool:
    await check_db_connection()
    result = (await db.query('DELETE type::thing("lecturers", $uuid) RETURN BEFORE;', {
        "uuid": uuid
    }))[0]["result"]

    return result[0] != None


async def close() -> None:
    await db.close()


# <(?!\/?(b|i|u|strong|em)(?=>|\s.*>))\/?.*?>
