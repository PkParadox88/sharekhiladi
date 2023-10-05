import json
from .session import SessionManager
from aiohttp import ClientSession, ClientError
import asyncio
import nest_asyncio
import logging

nest_asyncio.apply()

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

token_file = "khiladi/data_fetch/_tokens.json"


async def load_token():
    # Load file directly instead of calling SessionManager
    with open(token_file, 'r') as file:
        token_json = json.load(file)
    if "tokens" in token_json and token_json["tokens"]:
        tokens_dict = token_json["tokens"]
        return tokens_dict


async def get_live_data(session, tms_id, headers):
    url = f"https://{tms_id}.nepsetms.com.np/tmsapi/rtApi/ws/top25securities"
    logger.info(f"\tFetching {tms_id} data...")

    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            response_json = await response.json()
            data = response_json['payload']['data']
            # print(data)
            return data

    except ClientError as e:
        logger.error(f"AIOHTTP ClientError occurred: {e}")

    except Exception as e:
        logger.error(f"Error occurred during fetch_id: {e}")


async def main():
    async with ClientSession() as session:
        # asyncio.run(SessionManager().get_sessions()) # Refresh token
        auth_tokens = asyncio.run(load_token())
        # print(auth_tokens)

        for ids in auth_tokens:
            tms_id = auth_tokens[ids]['Referer'][8:13]
            headers = auth_tokens[ids]
            data = await get_live_data(session, tms_id, headers)
            return data
