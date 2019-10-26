import json

from guillotina import testing
from guillotina.tests.fixtures import ContainerRequesterAsyncContextManager

import pytest


def base_settings_configurator(settings):
    if "applications" in settings:
        settings["applications"].append("fianchetto")
    else:
        settings["applications"] = ["fianchetto"]


testing.configure_with(base_settings_configurator)


class fianchetto_Requester(ContainerRequesterAsyncContextManager):  # noqa
    async def __aenter__(self):
        await super().__aenter__()
        resp = await self.requester(
            "POST",
            "/db/guillotina/@addons",
            data=json.dumps({"id": "fianchetto"}),
        )
        return self.requester


@pytest.fixture(scope="function")
async def fianchetto_requester(guillotina):
    return fianchetto_Requester(guillotina)
