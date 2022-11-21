from os import environ
import asyncio
from autobahn.wamp.types import ComponentConfig
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

import uuid
import time

IS_MAIN = bool(environ.get("VOLPY_TCP_MAIN", False))
ROUTER_URL = environ.get("VOLPY_ROUTER", "ws://127.0.0.1:8080/ws")
REALM = "Volpy"
volpy_tcp = None

class VolpyTCP(ApplicationSession):
    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.init()

    def init(self):
        self.uuid2id = {}
        self.id2uuid = {}
        self.uuid = str(uuid.uuid4())
        self.id = None
        self.callback = {}
        self.heartbeat = {}
        self.callback["0"] = lambda x: x

    async def onJoin(self, details):
        if self.id:
            # Already init
            return
        if IS_MAIN:
            print("Setup for main")
            await self.register(self._node_register_d, 'com.node.register')
            await self.register(self._node_unregister_d, 'com.node.unregister')
            await self.register(self._node_sync_d, 'com.node.sync')
            await self.subscribe(self._heartbeatMain_d, 'com.heartbeat.report')
        else:
            self.id = await self.call('com.node.register', self.uuid)
            await self.register(self.recv, f'com.exec.node{self.id}')
            await self.subscribe(self._heartbeat_d, 'com.heartbeat.update')

    async def onLeave(self, details):
        if not IS_MAIN:
            self.id = await self.call('com.node.unregister', self.uuid)

    async def _node_register_d(self, uuid):
        if uuid in self.uuid2id:
            id = self.uuid2id(uuid)
            return id
        else:
            # Generate id for node
            id = str(len(self.uuid2id))
            self.uuid2id[uuid] = id
            self.id2uuid[id] = uuid
            print(f'Reg: {id}')
            await self._heartbeatMain_d(id) # Also update heartbeat of that node
            return id

    async def _node_unregister_d(self, uuid):
        if uuid in self.uuid2id:
            id = self.uuid2id(uuid)
            del self.uuid2id[uuid]
            del self.id2uuid[id]
            print(f'Unreg: {id}')

    async def _node_sync_d(self):
        return list(self.id2uuid.items())

    async def _heartbeatMain_d(self, id):
        # Main receiving heartbeat
        self.heartbeat[id] = int(time.time())
        data = {"uuid2id": self.uuid2id, "heartbeat": self.heartbeat}
        self.publish('com.heartbeat.update', data)

    async def _heartbeat_d(self, data):
        # Node receiving update from heartbeat (publish from main)
        print(f'{self.id} hbt update: {data}')
        self.uuid2id = data["uuid2id"]
        self.id2uuid = dict(zip(self.uuid2id.values(), self.uuid2id.keys()))
        self.heartbeat = data["heartbeat"]

    async def sync_nodeid_list(self):
        self.id2uuid = await self.call('com.node.sync')
        return self.id2uuid

    async def get_nodeid_list(self):
        return list(self.id2uuid.keys())

    def setCallback(self, t, callback):
        self.callback[t] = callback

    async def recv(self, msg):
        print(f'{self.id} recv: {msg}')
        msgType, data = msg["msgType"], msg["data"]
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        f = self.callback[msgType]
        f(data)

    async def send(self, id, msgType, data):
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        msg = { "msgType": msgType,
                "data": data}
        return await self.call(f'com.exec.node{id}', msg)

    async def broadcast(self, msgType, data):
        print(f'{self.id} broadcast: {data}')
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        msg = { "msgType": msgType,
                "data": data}
        tasks = []
        for id in self.id2uuid.keys():
            if id == self.id:
                continue
            print(f"Send: {id}, {msg}")
            t = self.call(f'com.exec.node{id}', msg)
            print(type(t))
            tasks.append(t)
        await asyncio.gather(*tasks)

import aioconsole
async def task(session):
    loop = asyncio.get_event_loop()
    while True:
        await aioconsole.ainput("Enter to continue")
        await session.broadcast("0", "test")

def threadTask(session, loop):
    asyncio.set_event_loop(loop)
    asyncio.run_coroutine_threadsafe(task(session), loop)

from threading import Thread
if __name__ == '__main__':
    session = VolpyTCP(ComponentConfig(REALM, {}))
    runner = ApplicationRunner(ROUTER_URL, REALM)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if not IS_MAIN:
        thread = Thread(target=threadTask, args=(session,loop,))
        thread.start()
    runner.run(session, start_loop=True)