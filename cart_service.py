from sanic import Sanic
from sanic.response import json
import asyncpg

app = Sanic("Cart Service")
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


async def add_item_to_cart(user_id, item_id, quantity):
    async with db_pool.acquire() as connection:
        query = f"INSERT INTO cart (user_id, item_id, quantity) VALUES ({user_id}, {item_id}, {quantity}) " \
                f"ON CONFLICT (user_id, item_id) DO UPDATE SET quantity = cart.quantity + {quantity}"
        await connection.execute(query, user_id, item_id, quantity)


async def remove_item_from_cart(user_id, item_id):
    async with db_pool.acquire() as connection:
        query = f"DELETE FROM cart WHERE user_id = {user_id} AND item_id = {item_id}"
        await connection.execute(query, user_id, item_id)


async def update_item_quantity(user_id, item_id, quantity):
    async with db_pool.acquire() as connection:
        query = f"UPDATE cart SET quantity = {quantity} WHERE user_id = {user_id} AND item_id = {item_id}"
        await connection.execute(query, quantity, user_id, item_id)


async def get_cart_items(user_id):
    async with db_pool.acquire() as connection:
        query = f"""
            SELECT c.item_id, c.quantity, i.name, i.price 
            FROM cart c
            JOIN items i ON c.item_id = i.id
            WHERE c.user_id = {user_id}
        """
        return await connection.fetch(query, user_id)


@app.post("/api/cart")
async def add_item_to_cart_handler(request):
    data = request.json
    user_id = data.get("user_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity")

    await add_item_to_cart(user_id, item_id, quantity)

    return json({"message": "Item added to cart successfully"})


@app.delete("/api/cart")
async def remove_item_from_cart_handler(request):
    data = request.json
    user_id = data.get("user_id")
    item_id = data.get("item_id")

    await remove_item_from_cart(user_id, item_id)

    return json({"message": "Item removed from cart successfully"})


@app.put("/api/cart")
async def update_item_quantity_handler(request):
    data = request.json
    user_id = data.get("user_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity")

    await update_item_quantity(user_id, item_id, quantity)

    return json({"message": "Item quantity updated successfully"})


@app.get("/api/cart")
async def get_cart_items_handler(request):
    user_id = request.args.get("user_id")
    if not user_id:
        return json({"message": "User ID is required"}, status=400)

    items = await get_cart_items(user_id)
    return json({"cart": items})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)