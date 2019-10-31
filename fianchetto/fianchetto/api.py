import asyncio
import logging

import aiohttp
from aiohttp import web
from guillotina import configure
from guillotina.component import get_utility
from guillotina.transactions import get_tm
from guillotina.utils import get_authenticated_user_id

from fianchetto.content import IChessGame
from fianchetto.interfaces import IChessServerManager

logger = logging.getLogger("fianchetto")


@configure.service(
    context=IChessGame,
    method="GET",
    name="@play",
    permission="fianchetto.PlayGame",
)
async def play_chess_game(context, request):
    # Create new ws
    ws = web.WebSocketResponse()

    # Get utility that manages game messages
    utility = get_utility(IChessServerManager)
    player_id = get_authenticated_user_id()

    # TODO: get also the side from request and send to utility
    utility.register_player(ws, game=context, player_id=player_id)

    tm = get_tm()
    await tm.abort()
    await ws.prepare(request)

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.text:
                # send new moves to all ws connected to game
                await utility.queue_move(context, msg.data)
            elif msg.type == aiohttp.WSMsgType.error:
                logger.debug(
                    "ws connection closed with exception {0:s}".format(
                        ws.exception()
                    )
                )
    except (RuntimeError, asyncio.CancelledError):
        pass
    finally:
        logger.debug("websocket connection closed")
        utility.unregister_player(context, player_id, "white")

    return {}

@configure.service(
    context=IChessGame,
    method="GET",
    name="@simple",
    permission="fianchetto.PlayGame",
    allow_access=True,
)
async def simple_chessboard(context, request):
    """ This is a purposefully simple endpoint to demonstrate websockets.
        It is configured to rebroadcast incoming messagse to every client
        connected to the game.
    """
    ws = web.WebSocketResponse()
    utility = get_utility(IChessServerManager)
    utility.simple_chessboard_ws(ws, request, game=context)
    tm = get_tm()
    await tm.abort()
    await ws.prepare(request)
    try:
        async for message in ws:
            if message.type == aiohttp.WSMsgType.text:
                # This is where incoming messages are handled. 
                # This simple example just rebroadcasts incoming messages.
                await utility.broadcast_incoming_message(game=context, 
                                                         message=message)
            elif message.type == aiohttp.WSMsgType.error:
                logger.debug(
                    "ws connection closed with exception {0:s}".format(
                        ws.exception()
                    )
                )
    except (RuntimeError, asyncio.CancelledError):
        pass
    finally:
        logger.debug("websocket connection closed")
    return {}
