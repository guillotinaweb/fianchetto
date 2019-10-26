import asyncio
import json
import logging

from fianchetto.content import IChessGame

logger = logging.getLogger("fianchetto")


class ChessServerManager:
    """This async utility is responsible of sending messages for new
    chess moves at every registered game
    """

    def __init__(self, settings=None, loop=None):
        self._loop = loop
        self._settings = {}
        self._gamechannels: dict = {}

    def register_game(self, game: IChessGame):
        self._gamechannels[game.id] = {
            "white": None,
            "black": None,
            "observers": [],
        }

    def register_observer(self, ws, game: IChessGame):
        self._gamechannels[game.id]["observers"].append(ws)

    def initialize_game(self, game: IChessGame):
        self._gamechannels[game.id] = {
            "queue": asyncio.Queue(),
            "black": {"user_id": None, "ws": None},
            "white": {"user_id": None, "ws": None},
            "observers": [],  # list of websockets
        }

    def register_player(
        self, ws, game: IChessGame, player_id: str, side="white"
    ):
        if game.id not in self._gamechannels:
            self.initialize_game(game)

        self._gamechannels[game.id][side]["ws"] = ws
        self._gamechannels[game.id][side]["user_id"] = player_id

        # Schedule the function that
        asyncio.ensure_future(self.handle_game)

    def unregister_player(self, game: IChessGame, player_id, side):
        # Player left the game, so we just remove the websocket
        self._gamechannels[game.id][side].pop("ws", None)

    async def finalize(self):
        pass

    async def queue_move(self, game: IChessGame, move_message: str, side: str):
        queue = self._gamechannels[game.id]["queue"]
        message = {"side": side, "move": move_message}
        await queue.put(message)

    async def handle_game(self, game_id):
        # Get a new queue for the game
        queue = self._gamechannels[game_id]["queue"]
        while True:
            try:
                # Get new message
                message = await asyncio.wait_for(queue.get(), 0.2)
                # Handle new message in a queue
                move_side = message["side"]

                opponent_side = "black" if move_side == "white" else "white"
                opponent_ws = self._gamechannels[game_id][opponent_side]["ws"]
                observer_ws = self._gamechannels[game_id]["observers"]

                # Send notification to opponent and all observers
                for ws in [opponent_ws] + observer_ws:
                    await ws.send_str(json.dumps(message))

            except (
                RuntimeError,
                asyncio.CancelledError,
                asyncio.TimeoutError,
            ):
                pass
            except Exception:
                logger.warning("Error sending message", exc_info=True)
                await asyncio.sleep(1)

    async def initialize(self, app=None):
        while True:
            try:
                # Nothing to do on the main utility loop. All is
                # handled on each game handler tasks
                await asyncio.sleep(20)
            except (
                RuntimeError,
                asyncio.CancelledError,
                asyncio.TimeoutError,
            ):
                pass
