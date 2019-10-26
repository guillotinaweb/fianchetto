import asyncio
import logging

import aiohttp
from aiohttp import web
from guillotina import configure
from guillotina.component import get_utility
from guillotina.transactions import get_tm

from fianchetto.utility import IMessageSender

from .content import IChessGame

logger = logging.getLogger("fianchetto")


@configure.service(
    context=IChessGame,
    method="POST",
    name="@play",
    permission="fianchetto.PlayGame",
)
async def play_chess_game(context, request):
    ws = web.WebSocketResponse()
    utility = get_utility(IMessageSender)
    utility.register_ws(ws, request)

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
        utility.unregister_ws(ws)

    return {}
