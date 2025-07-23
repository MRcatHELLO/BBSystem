import asyncio
import websockets
import json
import os
import uuid

USERS_FILE = "users.json"
USERS = {}
MESSAGES = {}  # username: list of {from, body}

def load_users():
    global USERS
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            USERS = json.load(f)
    else:
        USERS = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(USERS, f)

async def handler(websocket, path):
    async for message in websocket:
        try:
            data = json.loads(message)
            if data.get("type") == "register":
                user = data.get("user")
                pwd = data.get("password")
                if not user or not pwd:
                    await websocket.send(json.dumps({
                        "type": "register_result",
                        "success": False,
                        "message": "Username and password required."
                    }))
                elif user in USERS:
                    await websocket.send(json.dumps({
                        "type": "register_result",
                        "success": False,
                        "message": "Username already exists."
                    }))
                else:
                    user_id = str(uuid.uuid4())
                    USERS[user] = {
                        "id": user_id,
                        "password": pwd
                    }
                    save_users()
                    await websocket.send(json.dumps({
                        "type": "register_result",
                        "success": True,
                        "user_id": user_id
                    }))
            elif data.get("type") == "login":
                user = data.get("user")
                pwd = data.get("password")
                user_data = USERS.get(user)
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
            elif data.get("type") == "send_message":
                to = data.get("to")
                from_user = data.get("from")
                body = data.get("body")
                if not to or not from_user or not body:
                    await websocket.send(json.dumps({
                        "type": "message_sent",
                        "success": False,
                        "message": "Missing fields."
                    }))
                elif to not in USERS:
                    await websocket.send(json.dumps({
                        "type": "message_sent",
                        "success": False,
                        "message": "Recipient does not exist."
                    }))
                else:
                    MESSAGES.setdefault(to, []).append({"from": from_user, "body": body})
                    await websocket.send(json.dumps({
                        "type": "message_sent",
                        "success": True
                    }))
            elif data.get("type") == "get_messages":
                user = data.get("user")
                msgs = MESSAGES.get(user, [])
                await websocket.send(json.dumps({
                    "type": "inbox",
                    "messages": msgs
                }))
            elif data.get("type") == "clear_inbox":
                user = data.get("user")
                if user in MESSAGES:
                    MESSAGES[user] = []
                    #save_messages()  # Only if you have a save_messages() function
                await websocket.send(json.dumps({
                    "type": "inbox_cleared"
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

async def main():
    load_users()
    ## Start the WebSocket server
    ## change the host and port as needed
    print("Starting WebSocket server...")
    print ("Press Ctrl+C to stop the server.")
    print ("if get an error and you did nothing try deleting the users.json file that ussally is in the same folder as this script.")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())