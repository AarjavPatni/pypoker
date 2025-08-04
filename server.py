import asyncio
import websockets
from dataclasses import dataclass
from main import Player, Table
import logging

connected = set()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
)

@dataclass
class Room:
    id: int
    table: Table
    players: dict[Player, websockets.ServerConnection]
    host: Player


rooms: dict[int, Room] = {}

async def handler(ws: websockets.ServerConnection):
    await ws.send("Enter your name:")
    name: str = str(await ws.recv())
    player: Player = Player(name, 1000)
    print(f"{player} is connected")
    
    if rooms:
        while True:
            await ws.send("Create (1) or join (2) a room?")
            create_or_join: int = int(await ws.recv())
            
            match create_or_join:
                case 1:
                    room_idx: int = len(rooms) + 1
                    table: Table = Table(10, 20)
                    room_players: dict[Player, websockets.ServerConnection] = {player: ws}
                    host: Player = player
                    new_room: Room = Room(room_idx, table, room_players, host)
                    rooms[room_idx] = new_room
                    
                    await ws.send(f"You are now the host of {room_idx}.")
                    logging.info(f"{player} created {room_idx}")
                
                case 2:
                    for idx, room in enumerate(rooms, start=1):
                        await ws.send(f"{idx}. {room}")
                    
                    room_choice_idx: int = int(await ws.recv())
                
                    while room_choice_idx is None:
                        await ws.send("Room doesn't exist. Please choose a valid room.")
                        room_choice_idx: int = int(await ws.recv())
                        
                    rooms[room_choice_idx].players[player] = ws
                    
                    existing_players_sockets: list[websockets.ServerConnection] = [rooms[room_choice_idx].players[p] for p in rooms[room_choice_idx].players]
                    
                    logging.info(f"{player} joined room {room_choice_idx}")
                    
                    # broadcast a message to everyone in the room
                    for socket in existing_players_sockets:
                        if socket is not ws:
                            await socket.send(f"{player} has joined the room")
                
                case _:
                    await ws.send("Invalid option. Please try again.")
                    continue
            
            break
    else:
        room_idx: int = len(rooms) + 1
        table: Table = Table(10, 20)
        room_players: dict[Player, websockets.ServerConnection] = {player: ws}
        host: Player = player
        new_room: Room = Room(room_idx, table, room_players, host)
        rooms[room_idx] = new_room
        
                            
        await ws.send(f"You are now the host of {room_idx}.")
        logging.info(f"{player} created {room_idx}")
        
    
    connected.add(ws)
    try:
        async for msg in ws:
            for conn in connected:
                if conn != ws:
                    await conn.send(msg)
    finally:
        # TODO: find the player in the Room and remove them
        connected.remove(ws)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())
