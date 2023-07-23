from sanic import Sanic
from sanic.response import json
import asyncpg

app = Sanic("Checkout Service")
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


async def calculate_total_price(user_id):
    async with db_pool.acquire() as connection:
        query = """
            SELECT SUM(i.price * c.quantity) AS total_price
            FROM cart c
            JOIN items i ON c.item_id = i.id
            WHERE c.user_id = "123";
        """
        return await connection.fetchval(query, user_id)


async def check_item_availability(user_id):
    async with db_pool.acquire() as connection:
        # Assuming we have a separate table for inventory with columns 'item_id' and 'stock'
        query = f"""
            SELECT c.item_id, c.quantity, i.name, i.stock
            FROM cart c
            JOIN items i ON c.item_id = i.id
            WHERE c.user_id = {user_id};
        """
        cart_items = await connection.fetch(query, user_id)
        
        # Check if the items are available in the inventory
        not_available_items = []
        for item in cart_items:
            if item['quantity'] > item['stock']:
                not_available_items.append(item['name'])

        return not_available_items


async def place_order(user_id):
    async with db_pool.acquire() as connection:
        query = f"""
            INSERT INTO orders (user_id, item_id, quantity)
            SELECT user_id, item_id, quantity FROM cart
            WHERE user_id = {user_id} 
        """
        await connection.execute(query, user_id)

        # Clear the cart after placing the order
        clear_cart_query = "DELETE FROM cart WHERE user_id = $1"
        await connection.execute(clear_cart_query, user_id)

        # Return the order ID or any other relevant information
        return json({"message": "Order placed successfully", "order_id": 12345})


@app.post("/api/checkout/total")
async def calculate_total_price_handler(request):
    data = request.json
    user_id = data.get("user_id")

    total_price = await calculate_total_price(user_id)
    return json({"total_price": total_price})


@app.post("/api/checkout/availability")
async def check_item_availability_handler(request):
    data = request.json
    user_id = data.get("user_id")

    not_available_items = await check_item_availability(user_id)
    if not_available_items:
        return json({"message": "Some items are not available", "not_available_items": not_available_items})
    else:
        return json({"message": "Items are available"})


@app.post("/api/checkout/order")
async def place_order_handler(request):
    data = request.json
    user_id = data.get("user_id")

    not_available_items = await check_item_availability(user_id)
    if not_available_items:
        return json({"message": "Some items are not available", "not_available_items": not_available_items})
    
    order_result = await place_order(user_id)
    return order_result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
