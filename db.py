from surrealdb import Surreal
from main import loop

db = Surreal()


async def init() -> None:
    await db.connect("http://localhost:8000/rpc")
    await db.use("test", "test")


def get_lecturers() -> list:
    lecturers = loop.run_until_complete(db.query("SELECT * OMIT id FROM lecturers FETCH tags;"))[0]["result"]
    return lecturers


def get_lecturer(uuid) -> dict or None:
    data = loop.run_until_complete(db.query("SELECT * OMIT id FROM lecturers WHERE uuid = $uuid FETCH tags;", {
        "uuid": uuid
    }))[0]["result"]

    return data[0] if len(data) > 0 else None


def post_lecturer() -> None:
    db.query("")


def delete_lecturer(uuid) -> None:
    """ reponse = loop.run_until_complete(db.query("DELETE FROM lecturers WHERE uuid = $uuid;", {
        "uuid": uuid
    }))
    return reponse """

async def close() -> None:
    await db.close()
