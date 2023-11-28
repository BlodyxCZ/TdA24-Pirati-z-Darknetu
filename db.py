from surrealdb import Surreal

db = Surreal()

async def init():
    await db.connect("http://localhost:8000/rpc")
    await db.use("test", "test")

async def get_lecturers() -> dict:
    data = await db.query("SELECT * OMIT id FROM lecturers FETCH tags;")
    return data[0]

async def close():
    await db.close()