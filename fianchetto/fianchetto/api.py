import asyncio
import logging

import aiohttp
from aiohttp import web
from guillotina import configure
from guillotina.component import get_utility
from guillotina.response import HTTPPreconditionFailed
from guillotina.transactions import get_tm
from guillotina.utils import get_authenticated_user_id

from fianchetto.content import IChessGame
from fianchetto.interfaces import IChessServerManager
from fianchetto.utility import ChessServerManager

logger = logging.getLogger("fianchetto")


@configure.service(
    context=IChessGame,
    method="POST",
    name="@move",
    permission="fianchetto.PlayGame",
)
async def move(context, request):
    """
    Endpoint to make moves
    """
    move: str = await request.text()
    player_id: str = get_authenticated_user_id()
    side: str = context.get_side(player_id)

    move = translate_move(move)

    if context.turn != side:
        raise HTTPPreconditionFailed(content={"reason": "Not your move!"})

    if not context.valid_move(move):
        raise HTTPPreconditionFailed(content={"reason": "Invalid move"})

    utility: ChessServerManager = get_utility(IChessServerManager)
    await utility.queue_move(context, move, side=side)

    # Append new move
    moves = context.moves or []
    moves.append(move)
    context.moves = moves
    context.register()


def translate_move(move):
    # TODO: translate from front-end move languate to the language we
    # need to validate moves.
    return move


@configure.service(
    context=IChessGame,
    method="POST",
    name="@play",
    permission="fianchetto.PlayGame",
)
async def play_chess_game(context, request):
    # Create new ws
    ws = web.WebSocketResponse()

    # Get utility that manages game messages
    utility = get_utility(IChessServerManager)
    player_id = get_authenticated_user_id()

    utility.register_player(ws, game=context, player_id=player_id)

    tm = get_tm()
    await tm.abort()
    await ws.prepare(request)

    try:
        async for msg in ws:
            if msg.tp == aiohttp.WSMsgType.text:
                # ws does not receive any messages, just sends
                pass
            elif msg.tp == aiohttp.WSMsgType.error:
                logger.debug(
                    "ws connection closed with exception {0:s}".format(
                        ws.exception()
                    )
                )
    except (RuntimeError, asyncio.CancelledError):
        pass
    finally:
        logger.debug("websocket connection closed")
        utility.unregister_player(player_id)

    return {}
