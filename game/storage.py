import sys
from pathlib import Path
from asyncio import Queue, run
import asyncio
from enum import Enum
from pygbag.aio.fetch import RequestHandler
if sys.platform == "emscripten":
    from platform import window
else:
    import requests
    import threading
    from base64 import urlsafe_b64encode as b64encode

storage: dict[str, str] = {}
http = RequestHandler()

class HttpTask(Enum):
    READ = 0
    WRITE = 1
    EXIT = 2

http_tasks: Queue[tuple[HttpTask, str, str]] = Queue()

def run_async_in_thread(coro):
    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)
        loop.close()

    thread = threading.Thread(target=runner)
    thread.start()
    return thread

async def execute_http_tasks() -> None:
    while True:
        try:
            async with asyncio.timeout(1):
                task_type, key, data = await http_tasks.get()
        except TimeoutError:
            continue
        if task_type is HttpTask.READ:
            storage[key] = await aread_data(key)
        elif task_type is HttpTask.WRITE:
            storage[key] = data
            await asave_data(key, data)
        else:
            break

async def asave_data(key: str, data: str) -> None:
    if sys.platform != "emscripten":
        requests.post(f"https://tlds1.warp.thecommcraft.de/storage/file/{key}/", data=data, timeout=10)
        return
    await http.post(f"https://tlds1.warp.thecommcraft.de/storage/file/{key}/", data=data)
    
async def aread_data(key: str) -> str:
    if sys.platform != "emscripten":
        return requests.get(f"https://tlds1.warp.thecommcraft.de/storage/file/{key}/", timeout=10).text
    return await http.get(f"https://tlds1.warp.thecommcraft.de/storage/file/{key}/")

def exit_executor():
    http_tasks.put_nowait((HttpTask.EXIT, "", ""))

def save_data(key: str, data: str) -> None:
    http_tasks.put_nowait((HttpTask.WRITE, key, data))

def read_data(key: str) -> str:
    http_tasks.put_nowait((HttpTask.READ, key, ""))
    return storage.get(key) or ""

def old_save_data(key: str, data: str) -> None:
    if sys.platform == "emscripten":
        window.localStorage.setItem(key, data) # For browser support
    else:
        (
            Path(__file__).parent /
            "storage" /
            b64encode(key.encode()).decode() # This way, any string can be accepted. ("/" and others won't cause problems.)
        ).write_text(data)
        
def old_read_data(key: str) -> str:
    if sys.platform == "emscripten":
        return window.localStorage.getItem(key) or "" # Return "" if nothing is stored
    else:
        try:
            return (Path(__file__).parent / "storage" / b64encode(key.encode()).decode()).read_text()
        except Exception:
            return ""