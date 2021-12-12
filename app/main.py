import asyncio
import logging
import traceback
from asyncio import AbstractEventLoop
from typing import Optional

import config
from client.options import StatusOptions
from client.status import StatusClient


# Run Client Forever :D
class RunClient:
    __START_RETRY_INTERVAL = 30
    __UPDATE_RESOURCE_INTERVAL = 15

    def __init__(self, client_id: str, status_options: StatusOptions, loop: AbstractEventLoop):
        self.client_id: str = client_id
        self.status_options: StatusOptions = status_options
        self.loop: AbstractEventLoop = loop
        self.client: Optional[StatusClient] = None
        self.loop.create_task(self.__update_options())

    async def __update_options(self):
        while True:
            try:
                await status_options.update_options()
            except:
                logging.error(traceback.format_exc())
            await asyncio.sleep(self.__UPDATE_RESOURCE_INTERVAL)

    async def __start_client(self):
        await asyncio.sleep(5)
        try:
            self.client = StatusClient(
                client_id=self.status_options.client_id,
                options=self.status_options
            )
        except Exception as ex:
            print(f"Failed to start, retrying in {self.__START_RETRY_INTERVAL} seconds -> {ex}")
            await asyncio.sleep(self.__START_RETRY_INTERVAL)
            await self.__start_client()

    async def run(self):
        await self.__start_client()

        try:
            await self.client.run_loop()
        except Exception as ex:
            print(f"RPC Closed, retrying in {self.__START_RETRY_INTERVAL} seconds -> {ex}")
            await asyncio.sleep(self.__START_RETRY_INTERVAL - 5)
            await self.run()


# Start everything :D
loop = asyncio.get_event_loop()
status_options: StatusOptions = StatusOptions(config.api_url, config.auth_key)
client: RunClient = RunClient(config.client_id, status_options, loop)
loop.run_until_complete(client.run())
