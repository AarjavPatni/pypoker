import asyncio
import websockets
from dataclasses import dataclass
from main import Player, Table
import logging
from typing import Optional

connected = set()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@dataclass
class Room:
    id: int
    table: Table
    player_socks: dict[websockets.ServerConnection, Player]
    host: Player


rooms: dict[int, Room] = {}


async def handler(ws: websockets.ServerConnection):
    await ws.send("Enter your name:")
    name: str = str(await ws.recv())
    player: Player = Player(name, 1000)
    room_idx: int
    print(f"{player} is connected")

    if rooms:
        while True:
            await ws.send("Create (1) or join (2) a room?")
            create_or_join: int = int(await ws.recv())

            match create_or_join:
                case 1:
                    room_idx = len(rooms) + 1
                    table: Table = Table(10, 20)
                    current_player_sock: dict[websockets.ServerConnection, Player] = {
                        ws: player
                    }
                    host: Player = player
                    new_room: Room = Room(room_idx, table, current_player_sock, host)
                    rooms[room_idx] = new_room

                    await ws.send(f"You are now the host of {room_idx}.")
                    logging.info(f"{player} created {room_idx}")

                case 2:
                    for idx, room in enumerate(rooms, start=1):
                        await ws.send(f"{idx}. {room}")

                    room_choice_idx = int(await ws.recv())

                    while room_choice_idx not in rooms:
                        await ws.send("Room doesn't exist. Please choose a valid room.")
                        room_choice_idx: int = int(await ws.recv())

                    rooms[room_choice_idx].player_socks[ws] = player

                    existing_players_socks: list[websockets.ServerConnection] = [
                        sock for sock in rooms[room_choice_idx].player_socks
                    ]

                    logging.info(f"{player} joined room {room_choice_idx}")

                    # broadcast a message to everyone in the room
                    for socket in existing_players_socks:
                        if socket is not ws:
                            await socket.send(f"{player} has joined the room")

                case _:
                    await ws.send("Invalid option. Please try again.")
                    continue

            break
    else:
        room_idx = len(rooms) + 1
        table: Table = Table(10, 20)
        current_player_sock: dict[websockets.ServerConnection, Player] = {ws: player}
        host: Player = player
        new_room: Room = Room(room_idx, table, current_player_sock, host)
        rooms[room_idx] = new_room

        await ws.send(f"You are now the host of {room_idx}.")
        logging.info(f"{player} created {room_idx}")

    connected.add(ws)
    try:
        async for msg in ws:
            print(f"{player} - {msg}")
            match msg.strip():
                case "start":
                    await ws.send("Starting game...")
                    # find the room the ws is in, add all the players from that room on the table,
                    # then run the game
                    target_room: Optional[Room] = None

                    for room_idx in rooms:
                        if ws in rooms[room_idx].player_socks:
                            target_room = rooms[room_idx]
                            break

                    assert target_room is not None
                    for player in target_room.player_socks.values():
                        target_room.table.players.append(player)

                    target_room.table.begin_game()

                case _:
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
