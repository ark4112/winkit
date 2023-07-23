from sanic import Sanic
from sanic.response import json
import asyncpg

app = Sanic("Item Service")
db_pool = None

async def create_database_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="your_username",
        password="your_password",
        database="your_database"
    )

@app.listener('before_server_start')
async def setup_db(app, loop):
    await create_database_pool()

@app.listener('after_server_stop')
async def close_db(app, loop):
    await db_pool.close()

async def get_all_items():
    async with db_pool.acquire() as connection:
        query = "SELECT * FROM items"
        return await connection.fetch(query)

async def get_items_by_category(category):
    async with db_pool.acquire() as connection:
        query = "SELECT * FROM items WHERE category = $1"
        return await connection.fetch(query, category)

async def get_item_details(item_id):
    async with db_pool.acquire() as connection:
        query = "SELECT * FROM items WHERE id = $1"
        return await connection.fetchrow(query, item_id)

@app.get("/api/items")
async def get_all_items_handler(request):
    items = await get_all_items()
    return json({"items": items})

@app.get("/api/items/<category>")
async def get_items_by_category_handler(request, category):
    items = await get_items_by_category(category)
    return json({"items": items})

@app.get("/api/items/<item_id>")
async def get_item_details_handler(request, item_id):
    item = await get_item_details(item_id)
    if item:
        return json({"item": item})
    else:
        return json({"message": "Item not found"}, status=404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
