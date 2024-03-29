from surrealdb import Surreal, ws
import os
import re
import bcrypt

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
    lecturers = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id, username, password FROM lecturers;"))[0]["result"]
    
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

async def get_all_locations() -> list:
    await check_db_connection()
    locations = (await db.query("RETURN array::distinct(SELECT VALUE location FROM lecturers);"))[0]["result"]

    return locations

async def get_all_tags() -> list:
    await check_db_connection()
    tags = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM tags;"))[0]["result"]

    return tags

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
    data["bio"] = re.sub(r"<(?!\/?(b|i|u|strong|em|a|p|br|li|ul|ol)(?=>|\s.*>))\/?.*?>", "", data["bio"]) # remove unallowed HTML tags
    
    if "tags" in data:
        tags = []
        for tag in data["tags"]:
            tags.append((await db.query("IF (SELECT * FROM tags WHERE name = $tag) = [] THEN SELECT VALUE id FROM (CREATE tags:uuid() SET name = $tag); ELSE SELECT VALUE id FROM tags WHERE name = $tag; END;", vars={
                "tag": tag["name"]
            }))[0]["result"][0])

        data["tags"] = tags
    else:
        data["tags"] = []
    
    data["password"] = bcrypt.hashpw(bytes(data["password"], "utf-8"), bcrypt.gensalt()).decode()
    data["recieve_email"] = True

    lecturer = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id, tags FROM (CREATE lecturers:uuid() CONTENT $data);", vars={
        "data": data
    }))[0]["result"][0]

    lecturer["tags"] = (await db.query("SELECT *, meta::id(id) AS uuid OMIT id FROM $tags", vars={
        "tags": data["tags"]
    }))[0]["result"]
    
    return lecturer


async def login(data: dict) -> dict:
    await check_db_connection()
    
    lecturer = (await db.query("SELECT password, meta::id(id) AS uuid FROM lecturers WHERE username = $username;", vars={
        "username": data["username"]
    }))[0]["result"]

    if len(lecturer) == 0:
        return {"code": 401, "message": "Invalid username"}

    password_salted = lecturer[0]["password"]

    if not bcrypt.checkpw(data["password"].encode(), password_salted.encode()):
        return {"code": 401, "message": "Invalid password"}

    token = (await db.query("CREATE logins CONTENT {lecturer: type::thing('lecturers', $lecturer), session_token: rand::uuid::v7(), datetime: time::now(), expiry_date: time::now() + 2d} RETURN session_token;", vars={
        "lecturer": lecturer[0]["uuid"],
    }))[0]["result"][0]["session_token"]

    return {"code": 200, "message": "Logged in", "token": token, "uuid": lecturer[0]["uuid"]}


async def change_password(uuid, old_password, new_password) -> bool:
    await check_db_connection()

    lecturer = (await db.query("SELECT password FROM lecturers WHERE id = type::thing('lecturers', $uuid);", vars={
        "uuid": uuid
    }))[0]["result"]

    if len(lecturer) == 0:
        return False
    
    password_salted = lecturer[0]["password"]

    if not bcrypt.checkpw(old_password.encode(), password_salted.encode()) :
        return False
    
    new_password = bcrypt.hashpw(bytes(new_password, "utf-8"), bcrypt.gensalt()).decode()

    success = (await db.query("UPDATE type::thing('lecturers', $uuid) SET password = $new_password;", vars={
        "uuid": uuid,
        "new_password": new_password
    }))[0]["result"]

    return success != []
    

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


async def get_reservations(uuid, full) -> list or None:
    await check_db_connection()

    if full:
        result = (await db.query('IF (SELECT * FROM lecturers WHERE id = type::thing("lecturers", $uuid)) = [] THEN RETURN null; ELSE RETURN (SELECT *, meta::id(tag) AS tag, meta::id(id) AS uuid OMIT id, lecturer FROM reservations WHERE lecturer = type::thing("lecturers", $uuid)) END;', {
            "uuid": uuid
        }))[0]["result"]
    else:
        result = (await db.query('IF (SELECT * FROM lecturers WHERE id = type::thing("lecturers", $uuid)) = [] THEN RETURN null; ELSE RETURN (SELECT * OMIT id, lecturer, tag, confirmed, info, student FROM reservations WHERE lecturer = type::thing("lecturers", $uuid)) END;', {
            "uuid": uuid
        }))[0]["result"]

    return result


async def get_reservations_in_date(uuid, date) -> list or None:
    await check_db_connection()

    # Date format: "2021-05-01"
    result = (await db.query('IF (SELECT * FROM lecturers WHERE id = type::thing("lecturers", $uuid)) = [] THEN RETURN null; ELSE RETURN (SELECT *, meta::id(tag) AS tag, meta::id(id) AS uuid OMIT id FROM reservations WHERE (string::startsWith(start_date, $date) OR string::startsWith(end_date, $date)) AND lecturer = type::thing("lecturers", $uuid)) FETCH lecturer END;', vars={
        "uuid": uuid,
        "date": date
    }))[0]["result"]

    return result


async def post_reservation(data) -> dict:
    await check_db_connection()

    reservation = (await db.query('SELECT *, meta::id(tag) AS tag OMIT id, lecturer, confirmed FROM (CREATE reservations:uuid() CONTENT {"lecturer": type::thing("lecturers", $uuid), "tag": type::thing("tags", $tag), "start_date": $start_date, "end_date": $end_date, "student": $student, "info": $info, "confirmed": false});', vars={
        "uuid": data["uuid"],
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "info": data["info"],
        "tag": data["tag"],
        "student": data["student"]
    }))[0]["result"][0]

    return reservation


async def confirm_reservation(lecturer_uuid, reservation_uuid) -> bool:
    await check_db_connection()

    success = (await db.query('UPDATE reservations SET confirmed = true WHERE id = type::thing("reservations", $reservation_uuid) AND lecturer = type::thing("lecturers", $lecturer_uuid);', vars={
        "reservation_uuid": reservation_uuid,
        "lecturer_uuid": lecturer_uuid
    }))[0]["result"]

    return success != []


async def get_lecturer_uuid_from_token(token) -> str or None:
    await check_db_connection()
    
    uuid = (await db.query('SELECT VALUE meta::id(lecturer) FROM logins WHERE session_token = $session_token AND time::now() < expiry_date;', vars={
        "session_token": token
    }))[0]["result"]

    return None if uuid == [] else uuid[0]


async def delete_reservation(lecturer_uuid, reservation_uuid) -> dict or None:
    await check_db_connection()

    reservation = (await db.query('SELECT * FROM (DELETE type::thing("reservations", $reservation_uuid) WHERE lecturer = type::thing("lecturers", $lecturer_uuid) RETURN BEFORE) FETCH lecturer;', vars={
        "reservation_uuid": reservation_uuid,
        "lecturer_uuid": lecturer_uuid
    }))[0]["result"]

    return reservation


async def post_free_time(lecturer_uuid, data) -> dict or None:
    await check_db_connection()

    free_time = (await db.query('SELECT *, meta::id(id) AS uuid, meta::id(lecturer) AS lecturer OMIT id FROM (CREATE free_times:uuid() CONTENT {lecturer: type::thing("lecturers", $uuid), start_date: $start_date, end_date: $end_date});', vars={
        "uuid": lecturer_uuid,
        "start_date": data["start_date"],
        "end_date": data["end_date"]
    }))[0]["result"]

    return free_time


async def get_free_times(lecturer_uuid) -> list:
    await check_db_connection()

    free_times = (await db.query('SELECT *, meta::id(id) AS uuid, meta::id(lecturer) AS lecturer OMIT id FROM free_times WHERE lecturer = type::thing("lecturers", $uuid);', vars={
        "uuid": lecturer_uuid
    }))[0]["result"]

    return free_times


async def toggle_email_recieve(lecturer_uuid, value: bool) -> bool:
    await check_db_connection()

    success = (await db.query('UPDATE type::thing("lecturers", $uuid) SET recieve_email = $value;', vars={
        "uuid": lecturer_uuid,
        "value": value
    }))[0]["result"]

    return success != []

async def delete_free_time(lecturer_uuid, free_time_uuid) -> bool:
    await check_db_connection()

    success = (await db.query('DELETE type::thing("free_times", $free_time_uuid) WHERE lecturer = type::thing("lecturers", $lecturer_uuid) RETURN BEFORE;', vars={
        "free_time_uuid": free_time_uuid,
        "lecturer_uuid": lecturer_uuid
    }))[0]["result"]

    return success != []


async def get_reservation_by_uuid(uuid) -> dict:
    await check_db_connection()

    reservation = (await db.query('SELECT * FROM type::thing("reservations", $uuid) FETCH lecturer;', vars={
        "uuid": uuid
    }))[0]["result"][0]

    return reservation


async def check_availability_reservations(uuid, start_date, end_date) -> bool:
    await check_db_connection()

    availability = (await db.query('RETURN array::len(SELECT * FROM reservations WHERE lecturer = type::thing("lecturers", $uuid) AND (start_date >= $end_new OR end_date <= $start_new)) == array::len(SELECT * FROM reservations WHERE lecturer = type::thing("lecturers", $uuid));', vars={
        "uuid": uuid,
        "start_new": start_date,
        "end_new": end_date
    }))[0]["result"]

    return availability


async def check_availability_free_times(uuid, start_date, end_date) -> bool:
    await check_db_connection()

    availability = (await db.query('RETURN array::len(SELECT * FROM free_times WHERE lecturer = type::thing("lecturers", $uuid) AND (start_date <= $start_new AND end_date >= $end_new)) >= 1;', vars={
        "uuid": uuid,
        "start_new": start_date,
        "end_new": end_date
    }))[0]["result"]

    return availability


async def close() -> None:
    await db.close()


# <(?!\/?(b|i|u|strong|em|a|p|br|li|ul|ol)(?=>|\s.*>))\/?.*?>
