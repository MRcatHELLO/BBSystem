import asyncio
import websockets
import json
import uuid
from tinydb import TinyDB, Query

DB_FILE = "bbs_db.json"
db = TinyDB(DB_FILE)
users_table = db.table("users")
messages_table = db.table("messages")
public_table = db.table("public_posts")
money_table = db.table("money")

def get_user(username):
    User = Query()
    return users_table.get(User.username == username)

def add_user(username, password):
    user_id = str(uuid.uuid4())
    users_table.insert({"username": username, "password": password, "id": user_id, "balance": ""})
    money_table.insert({"username": username, "balance": 0})
    return user_id

def update_user_password(username, new_password):
    User = Query()
    users_table.update({"password": new_password}, User.username == username)

def add_message(to, from_user, body):
    messages_table.insert({"to": to, "from": from_user, "body": body})

def get_messages(username):
    Message = Query()
    return messages_table.search(Message.to == username)

def clear_inbox(username):
    Message = Query()
    messages_table.remove(Message.to == username)

def add_public_post(from_user, body):
    public_table.insert({"from": from_user, "body": body})

def get_public_posts(limit=50):
    posts = public_table.all()
    return posts[-limit:]

def update_balance(updated_balance):
    money_table.update({"balance": updated_balance})

def get_balance(username):
    field = Query()
    result = money_table.search(field.username == username)
    return result[0]['balance']

    


CONNECTED = set()

async def handler(websocket):
    CONNECTED.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                if msg_type == "public_post":
                    from_user = data.get("from")
                    body = data.get("body")
                    if not from_user or not body:
                        await websocket.send(json.dumps({
                            "type": "public_message",
                            "message": "Missing fields."
                        }))
                    else:
                        add_public_post(from_user, body)
                        for ws in CONNECTED:
                            try:
                                await ws.send(json.dumps({
                                    "type": "public_message",
                                    "message": f"{from_user}: {body}"
                                }))
                            except:
                                pass
                elif msg_type == "get_public_posts":
                    await websocket.send(json.dumps({
                        "type": "public_posts",
                        "posts": get_public_posts()
                    }))
                elif msg_type == "register":
                    user = data.get("user")
                    pwd = data.get("password")
                    if not user or not pwd:
                        await websocket.send(json.dumps({
                            "type": "register_result",
                            "success": False,
                            "message": "Username and password required."
                        }))
                    elif get_user(user):
                        await websocket.send(json.dumps({
                            "type": "register_result",
                            "success": False,
                            "message": "Username already exists."
                        }))
                    else:
                        user_id = add_user(user, pwd)
                        await websocket.send(json.dumps({
                            "type": "register_result",
                            "success": True,
                            "user_id": user_id
                        }))
                elif msg_type == "login":
                    user = data.get("user")
                    pwd = data.get("password")
                    user_data = get_user(user)
                    if user_data and user_data.get("password") == pwd:
                        await websocket.send(json.dumps({
                            "type": "login_result",
                            "success": True,
                            "user_id": user_data.get("id")
                        }))
                    else:
                        await websocket.send(json.dumps({
                            "type": "login_result",
                            "success": False
                        }))
                elif msg_type == "send_message":
                    to = data.get("to")
                    from_user = data.get("from")
                    body = data.get("body")
                    if not to or not from_user or not body:
                        await websocket.send(json.dumps({
                            "type": "message_sent",
                            "success": False,
                            "message": "Missing fields."
                        }))
                    elif not get_user(to):
                        await websocket.send(json.dumps({
                            "type": "message_sent",
                            "success": False,
                            "message": "Recipient does not exist."
                        }))
                    else:
                        add_message(to, from_user, body)
                        await websocket.send(json.dumps({
                            "type": "message_sent",
                            "success": True
                        }))
                elif msg_type == "get_messages":
                    user = data.get("user")
                    msgs = get_messages(user)
                    await websocket.send(json.dumps({
                        "type": "inbox",
                        "messages": msgs
                    }))
                elif msg_type == "clear_inbox":
                    user = data.get("user")
                    clear_inbox(user)
                    await websocket.send(json.dumps({
                        "type": "inbox_cleared"
                    }))
                    ## Update balance
                elif msg_type == "update_balance":
                    updated_balance = data.get("balance")
                    update_balance(updated_balance)
                    await websocket.send(json.dumps({
                        "type": "update_balance",
                        "success": True
                    }))
                elif msg_type == "get_balance":
                    username = data.get("user")
                    balance = get_balance(username)
                    await websocket.send(json.dumps({
                        "type": "server_balance",
                        "success": True,
                        "balance": balance
                    }))
                
                else:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Unknown command"
                    }))
            except Exception as e:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
    finally:
        CONNECTED.remove(websocket)

async def main():
    async with websockets.serve(handler, "127.0.0.1", 6509):
        print("WebSocket server started on ws://127.0.0.1:6509")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())