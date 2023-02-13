from os import environ
import asyncio
import uuid

import volpy_tcp
import volpy_driver
import volpy_worker

IS_MAIN = bool(environ.get("VOLPY_MAIN", False))
IS_NODE = bool(environ.get("VOLPY_NODE", False))
IS_DRIVER = bool(environ.get("VOLPY_DRIVER", False))

UUID = str(environ.get("UUID", uuid.uuid4()))

if __name__ == '__main__':
    if IS_MAIN:
        session, runner = Volpy_tcp.volpy_tcp_create_session_runner(UUID, is_main=True)
        runner.run(session, start_loop=True, log_level='info')
    elif IS_NODE:
        session, runner = Volpy_tcp.volpy_tcp_create_session_runner(UUID, is_main=False)
        worker = Volpy_worker.Worker(session)
        runner.run(session, start_loop=True, log_level='info')
    elif IS_DRIVER:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(volpy_driver.start_repl(loop,))
        loop.stop()
    else:
        print("Please set the running mode via env: VOLPY_MAIN, VOLPY_NODE, VOLPY_DRIVER")