# pypoker

A networked Texas Hold'em engine written in Python. Supports a full 6-player game over WebSockets, with hand evaluation, betting rounds, and a room-based lobby system.

## Structure

- `main.py` — all game logic: deck, hand evaluation, betting loop, round orchestration
- `server.py` — WebSocket server; handles room creation, player connections, and game start
- `tests.py` — unittest suite covering valid/invalid actions and all hand ranks

## Running

Start the server:

```bash
python server.py
```

The server listens on `localhost:8765`. Clients connect, choose a name, and either create or join a room. The room host sends `"start"` to begin the game.

Run tests:

```bash
python -m unittest tests.py
```

## Stack

Python 3.13, `asyncio`, `websockets`, `pyrefly` for type checking.

