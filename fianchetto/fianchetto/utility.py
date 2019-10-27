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
        if game.id not in self._gamechannels.keys():
            self.initialize_game(game)

        self._gamechannels[game.id][side]["ws"] = ws
        self._gamechannels[game.id][side]["user_id"] = player_id

        # Schedule the function that
        asyncio.ensure_future(self.handle_game(game.id))

    def unregister_player(self, game: IChessGame, player_id, side):
        # Player left the game, so we just remove the websocket
        self._gamechannels[game.id][side].pop("ws", None)

    def _get_all_ws_game(self, game_id: str):
        ws = []
        if self._gamechannels["black"].get("ws", None):
            ws.append(self._gamechannels["black"]["ws"])
        if self._gamechannels["white"].get("ws", None):
            ws.append(self._gamechannels["black"]["ws"]
        ws.extend(self._gamechannels["observers"])

        return ws

    async def finalize(self):
        pass

    async def queue_move(self, game: IChessGame, game_status: dict):
        queue = self._gamechannels[game.id]["queue"]
        message = {"status": game_status}
        await queue.put(message)

    async def handle_game(self, game_id):
        # Get a new queue for the game
        queue = self._gamechannels[game_id]["queue"]
        while True:
            try:
                # Get new message from the queue
                message = await asyncio.wait_for(queue.get(), 0.2)

                # Send message to all ws connected to a game
                for ws in self._get_all_ws_game(game_id):
                    await ws.send_str(message)

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
