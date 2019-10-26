import asyncio


async def test_install(fianchetto_requester):  # noqa
    async with fianchetto_requester as requester:
        response, _ = await requester('GET', '/db/guillotina/@addons')
        assert 'fianchetto' in response['installed']
