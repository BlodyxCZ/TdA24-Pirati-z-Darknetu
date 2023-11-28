from surrealdb import Surreal

db = Surreal()

async def init():
    await db.connect("http://localhost:8000/rpc")
    await db.use("test", "test")

async def get_lecturers():
    return await db.query("SELECT * OMIT id FROM lecturers FETCH tags;")

async def close():
    await db.close()