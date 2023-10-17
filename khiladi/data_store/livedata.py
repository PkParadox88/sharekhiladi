import time

from ..data_fetch import socket_data
from ..models import LiveIndex, LiveTable
from asgiref.sync import sync_to_async
import asyncio
import nest_asyncio

nest_asyncio.apply()


x = time.time()  # Initialize x


@sync_to_async()
def data_store(json_data):
    global x  # Make x a nonlocal variable
    LiveIndex.objects.all().delete()
    for data in json_data[0]['payload']['data']:
        LiveIndex.objects.create(**data)
    print("Live Index Data updated in Database")

    LiveTable.objects.all().delete()
    for data in json_data[1]['payload']['data']:
        LiveTable.objects.create(**data)
    print("Live Table Data updated in Database")

    diff = time.time() - x  # Calculate the time difference
    print(f"Time difference since the last update: {diff} seconds")
    x = time.time()  # Update x



async def main():
    try:
        data_queue = asyncio.Queue()
        asyncio.create_task(socket_data.main(data_queue))
        while True:
            json_data = await data_queue.get()  # Await the result
            # print(f"Received data: {json_data}")
            print("Received Data")
            print(time.time())
            await data_store(json_data)
            print(time.time())

    except asyncio.TimeoutError:
        print("Task timed out.")


async def fetch_and_store():
    await main()

# Usage:
# asyncio.run(get_data())  # Call get_data to start the main coroutine
