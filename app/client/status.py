import asyncio
import datetime
import os
import platform
import struct

from pypresence import AioPresence

from client.options import StatusOptions


class StatusClient(AioPresence):
    __UPDATE_INTERVAL: int = 16
    __RETRY_INTERVAL: int = 3

    def __init__(self, options: StatusOptions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options: StatusOptions = options
        self.client_id = str(self.client_id)

    async def connect(self):
        """
        Connect to IPC

        """

        print("-------------------")
        print(f"Connecting to IPC with Client ID {self.client_id}")

        await super(StatusClient, self).connect()

        print("-------------------")
        print(f"Connected to IPC with Client ID {self.client_id}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        print("-------------------")

    async def update(self, **kwargs):
        """
        Update status based on config

        """

        try:
            await super(StatusClient, self).update(**self.options.build())
            print("Updated presence @", datetime.datetime.utcnow())
        except struct.error:
            print("Failed to update presence, discord likely closed.")

    async def run_loop(self):
        """
        Update the custom status every interval

        """

        await self.connect()

        while True:
            await self.update()
            await asyncio.sleep(self.__UPDATE_INTERVAL)
