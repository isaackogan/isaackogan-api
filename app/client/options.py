import random

import aiohttp
import psutil


class StatusOptions:

    def __init__(self, api_url: str, authentication: str):
        self.__API_URL: str = api_url
        self.__AUTHENTICATION: str = authentication

        self._buttons = None
        self._details = []
        self._images = []
        self._client_id = "0"

    def build(self):
        return {
            "buttons": self.buttons,
            "details": self.detail,
            "state": self.state,
            "large_image": self.image
        }

    @property
    def client_id(self):
        return self._client_id

    @property
    def buttons(self):
        return self._buttons

    @property
    def detail(self):
        return random.choice(self._details) if len(self._details) > 0 else None

    @property
    def image(self):
        return random.choice(self._images) if len(self._images) > 0 else None

    @property
    def state(self):
        return f"RAM: {str(round(psutil.virtual_memory().percent, 1))}% CPU: {round(psutil.cpu_percent(), 1)}%"

    @staticmethod
    def __sanitize_request_options(data: dict) -> list:
        return list(data.values())

    async def update_options(self):
        async with aiohttp.ClientSession(headers={"Authorization": self.__AUTHENTICATION}) as session:
            # Get Client ID
            async with session.get(self.__API_URL + "/discord/rpc/client_id") as request:
                result = await request.json()
                if result is not None:
                    self._client_id = result

            # Get Quotes
            async with session.get(self.__API_URL + "/discord/rpc/quotes") as request:
                self._details = self.__sanitize_request_options(await request.json())

            # Get Images
            async with session.get(self.__API_URL + "/discord/rpc/images") as request:
                self._images = self.__sanitize_request_options(await request.json())

            # Get Buttons
            async with session.get(self.__API_URL + "/discord/rpc/buttons") as request:
                buttons: list = self.__sanitize_request_options(await request.json())
                self._buttons = buttons if len(buttons) > 0 else None
