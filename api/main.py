import asyncio
import logging
import os
import traceback
from asyncio import AbstractEventLoop

import aioredis
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel

import config
from modules import status

os.environ["FASTAPI_SIMPLE_SECURITY_DB_LOCATION"] = config.AUTH_SQL_FILE
from fastapi_simple_security import api_key_security, api_key_router

app = FastAPI(
    docs_url='/',
    redoc_url="/docs",
    title="Isaac Kogan API",
    description="Personal API for Isaac Kogan",
    version="1.0.0",
    openapi_url="/app-docs"
)

app.include_router(api_key_router, prefix="/auth", tags=["Authentication"])


async def update_images_task():
    while True:
        try:
            await status.update_images(config.IPC_APPLICATION_ID, config.IMAGES_PATH)
        except:
            logging.error(traceback.format_exc())

        await asyncio.sleep(config.UPDATE_IMAGE_INTERVAL)


@app.on_event("startup")
async def startup():
    redis = aioredis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(redis)

    loop: AbstractEventLoop = asyncio.get_event_loop()
    loop.create_task(update_images_task())


@app.get("/discord/rpc/quotes", tags=['Discord RPC (Quotes)'], dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_quote_list():
    return status.get_json_resource(config.QUOTES_PATH)


@app.put("/discord/rpc/quotes", tags=['Discord RPC (Quotes)'], dependencies=[Depends(api_key_security)])
async def put_quote(quote: str):
    return status.put_json_value(config.QUOTES_PATH, quote)


@app.patch("/discord/rpc/quotes", tags=['Discord RPC (Quotes)'], dependencies=[Depends(api_key_security)])
async def update_quote(key: str, replacement: str):
    return status.update_json_value(config.QUOTES_PATH, key, replacement)


@app.delete("/discord/rpc/quotes", tags=['Discord RPC (Quotes)'], dependencies=[Depends(api_key_security)])
async def update_quote(key: str):
    return status.delete_json_value(config.QUOTES_PATH, key)


@app.get("/discord/rpc/buttons", tags=['Discord RPC (Buttons)'], dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_button_list():
    return status.get_json_resource(config.BUTTONS_PATH)


class ButtonPayload(BaseModel):
    label: str
    url: str


@app.put("/discord/rpc/buttons", tags=['Discord RPC (Buttons)'], dependencies=[Depends(api_key_security)])
async def put_button(quote: ButtonPayload):
    return status.put_json_value(config.BUTTONS_PATH, quote)


@app.patch("/discord/rpc/buttons", tags=['Discord RPC (Buttons)'], dependencies=[Depends(api_key_security)])
async def update_button(key: str, replacement: ButtonPayload):
    return status.update_json_value(config.BUTTONS_PATH, key, replacement)


@app.delete("/discord/rpc/buttons", tags=['Discord RPC (Buttons)'], dependencies=[Depends(api_key_security)])
async def delete_button(key: str):
    return status.delete_json_value(config.BUTTONS_PATH, key)


@app.get("/discord/rpc/images", tags=['Discord RPC (General)'], dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_image_list():
    return status.get_json_resource(config.IMAGES_PATH)


@app.get("/discord/rpc/client_id", tags=['Discord RPC (General)'], dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_client_id():
    return config.IPC_APPLICATION_ID
