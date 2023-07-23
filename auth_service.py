from sanic import Sanic
from sanic.response import json
import asyncpg

app = Sanic("Authentication Service")
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

async def register_user(username, password):
    async with db_pool.acquire() as connection:
        query = "INSERT INTO users (username, password) VALUES ($1, $2)"
        await connection.execute(query, username, password)

async def get_user(username):
    async with db_pool.acquire() as connection:
        query = "SELECT username, password FROM users WHERE username = $1"
        return await connection.fetchrow(query, username)

@app.post("/api/register")
async def register(request):
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Check if the username is already taken
    existing_user = await get_user(username)
    if existing_user:
        return json({"message": "Username is already taken"}, status=409)

    # Create a new user
    await register_user(username, password)

    return json({"message": "User registered successfully"})


@app.post("/api/login")
async def login(request):
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Check if the user exists and the password is correct
    user = await get_user(username)
    if user and user['password'] == password:
        # Generate a session token
        token = generate_session_token(username)
        sessions[token] = username

        return json({"message": "User logged in successfully", "token": token})
    else:
        return json({"message": "Invalid username or password"}, status=401)


@app.post("/api/logout")
async def logout(request):
    token = request.headers.get("Authorization")

    # Check if the session token exists
    if token and token in sessions:
        del sessions[token]
        return json({"message": "User logged out successfully"})
    else:
        return json({"message": "Invalid session token"}, status=401)


def generate_session_token(username):
    # Generate a session token for the given username
    return f"SESSION_{username}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
