from .data_fetch import session, socket_data
from .data_store import livedata
from huey import crontab, CancelExecution
from huey.contrib.djhuey import periodic_task, task
import asyncio


@task()
def fetch_sessions():
    print("Session login...")
    asyncio.run(session.SessionManager().get_sessions())


@periodic_task(crontab(minute='*/1'))
def fetch_data():
    print("Fetching data...")
    timeout_seconds = 20  # Set the desired duration in seconds

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(run_with_timeout(timeout_seconds))
        return result
    except asyncio.TimeoutError:
        print("Task timed out.")
    # finally:
    #     raise CancelExecution()


async def run_with_timeout(timeout_seconds):
    task = asyncio.create_task(livedata.fetch_and_store())
    try:
        result = await asyncio.wait_for(task, timeout=timeout_seconds)
        return result
    except asyncio.TimeoutError:
        task.cancel()
        raise asyncio.TimeoutError

