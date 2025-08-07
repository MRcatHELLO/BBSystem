import os
import json
import asyncio
import websockets
import time

def telnet_client():
    url = input("Enter the WebSocket URL (e.g., ws://localhost:8765): ")
    fake_dialing()
    async def send_login():
        async with websockets.connect(url) as websocket:
            async def login():
                username = input("Username: ")
                password = input("Password: ")
                login_data = {"type": "login", "username": username, "password": password}
                await websocket.send(json.dumps(login_data))
                response = await websocket.recv()
                print(f"Response from server: {response}")
                return response

            response = await login()
            try:
                data = json.loads(response)
                if data.get("type") == "login_success":
                    print("Login successful!")
                    while True:
                        message = input("Enter your message (or 'exit' to quit): ")
                        if message.lower() == 'exit':
                            break
                        await websocket.send(json.dumps({
                            "type": "send_message",
                            "message": message
                        }))
                        response = await websocket.recv()
                        print(f"Response from server: {response}")
                else:
                    print("Login failed:", data.get("message", "Unknown error"))
            except Exception as e:
                print(f"An error occurred: {e}")
    asyncio.run(send_login())

def fake_dialing():
    print("Dialing out...", end="", flush=True)
    for _ in range(3):
        time.sleep(0.7)
        print(".", end="", flush=True)
    print("\nConnecting to BBS...")
    time.sleep(1)

def main():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print("Welcome to the pyterminal client!")
    print("type help for a list of commands.")
    print("type exit to quit.")
    while True:
        command = input("Enter command: ").strip().lower()
        if command == "telnet":
            telnet_client()
        elif command == "exit":
            print("Exiting the client.")
            break
        elif command == "help":
            print("Available commands:")
            print("telnet - Connect to a WebSocket server")
            print("exit - Exit the client")
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()
