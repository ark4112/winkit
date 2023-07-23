from sanic import Sanic
from sanic.response import json
import asyncpg

app = Sanic("Inventory Service")
db_pool = None


async def create_database_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="ark",
        password="aryan123",
        database="winkit_db"
    )


@app.listener('before_server_start')
async def setup_db(app, loop):
    await create_database_pool()


@app.listener('after_server_stop')
async def close_db(app, loop):
    await db_pool.close()


async def get_item_by_id(item_id):
    async with db_pool.acquire() as connection:
        query = "SELECT id, name, price, stock FROM items WHERE id = $1"
        return await connection.fetchrow(query, item_id)


@app.get("/api/inventory/<item_id:int>")
async def get_item_details_handler(request, item_id):
    item = await get_item_by_id(item_id)
    if item:
        return json({"item": item})
    else:
        return json({"message": "Item not found"}, status=404)


@app.post("/api/inventory")
async def add_item_to_inventory(request):
    data = request.json
    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")

    async with db_pool.acquire() as connection:
        query = f"INSERT INTO items (name, price, stock) VALUES ({name}, {price}, {stock}) RETURNING id"
        item_id = await connection.fetchval(query, name, price, stock)

    return json({"message": "Item added to inventory successfully", "item_id": item_id})


@app.put("/api/inventory/<item_id:int>")
async def update_item_in_inventory(request, item_id):
    data = request.json
    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")

    async with db_pool.acquire() as connection:
        query = f"UPDATE items SET name = {name}, price = {price}, stock = {stock} WHERE id = {item_id}"
        await connection.execute(query, name, price, stock, item_id)

    return json({"message": "Item updated in inventory successfully"})


@app.delete("/api/inventory/<item_id:int>")
async def delete_item_from_inventory(request, item_id):
    async with db_pool.acquire() as connection:
        query = f"DELETE FROM items WHERE id = {item_id}"
        await connection.execute(query, item_id)

    return json({"message": "Item deleted from inventory successfully"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)