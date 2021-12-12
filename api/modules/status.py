import json
from typing import List, Union, Any

import aiohttp


def get_json_resource(file_path: str):
    try:
        with open(file_path, encoding='utf-8') as file:
            data: dict = json.loads(file.read())
            return data
    except:
        return []


def __put_json_resource(file_path: str, data: Union[dict, list]):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=4))
    except:
        pass


async def update_images(client_id: str, images_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://discord.com/api/oauth2/applications/{client_id}/assets") as request:
            try:
                images: List[str] = [
                    resource.get("name") for resource in await request.json() if resource.get("name") is not None
                ]

                images_dict: dict = dict()

                for idx, image in enumerate(images):
                    images_dict[str(idx + 1)] = image

                __put_json_resource(images_path, images_dict)

            except:
                pass


def put_json_value(resource_path: str, value: Any) -> dict:
    current: dict = get_json_resource(resource_path)
    current[max(int(key) for key in current.keys()) + 1 if len(current.keys()) > 0 else 1] = value
    __put_json_resource(resource_path, current)
    return current


def update_json_value(resource_path: str, key: str, value: Any) -> dict:
    current: dict = get_json_resource(resource_path)
    current[key] = value
    __put_json_resource(resource_path, current)
    return current


def delete_json_value(resource_path: str, key: str) -> dict:
    current: dict = get_json_resource(resource_path)
    try:
        del current[key]
    except KeyError:
        pass
    __put_json_resource(resource_path, current)
    return current
