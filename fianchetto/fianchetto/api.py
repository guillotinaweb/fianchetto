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
