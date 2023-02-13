import asyncio
from autobahn.asyncio.wamp import ApplicationSession

from bidict import bidict
import typing

class SimpleWS(ApplicationSession):
    def __init__(self, config):
        ApplicationSession.__init__(self, config)

    def init(self, uuid, is_main=False):
        self.is_main = is_main
        self.id2uuid = bidict()
        self.id2sid = bidict()
        self.heartbeatlist = {}
        self.uuid = uuid
        self.id = None
        self.callback = {}
        self.heartbeat = {}
        self.callback["0"] = lambda x: x

    async def onJoin(self, details):
        if self.id != None:
            # Already init
            return
        self.log.info('Setup UUID: {uuid}', uuid=self.uuid)
        if self.is_main:
            await self.register(self._node_register_d, 'com.node.register')
            await self.subscribe(self._node_unregister_d, 'wamp.session.on_leave')
            await self.register(self._node_heartbeat_d, 'com.node.update_heartbeat')
            self.log.info("Setup Main finish")
        else:
            '''
            Subscribe for heartbeat first so when we register the node, 
            we can get heartbeat update right away
            '''
            await self.subscribe(self._cluster_heartbeat_d, 'com.cluster.heartbeat')
            self.id = await self.call('com.node.register', self._session_id, self.uuid)
            await self.register(self.recv, f'com.node{self.id}.call')
            self.log.info(f'Setup Node finish: sid_{self._session_id} id_{self.id}')

    async def _node_register_d(self, sid, uuid):
        if uuid in self.id2uuid.inverse:
            id = self.id2uuid.inverse[uuid]
            return id
        else:
            # Generate id for node
            id = str(len(self.id2uuid))
            self.id2uuid[id] = uuid
            self.id2sid[id] = sid
            self.log.info(f'Reg: {id}, {sid}')
            await self._cluster_update_call()
            return id

    async def _node_unregister_d(self, sid):
        if sid in self.id2sid.inverse:
            id = self.id2sid.inverse[sid]
            self.log.info(f'Unreg: {id}, {sid}')
            del self.id2uuid[id]
            del self.id2sid[id]
            await self._cluster_update_call()

    async def _cluster_update_call(self):
        set_id2uuid = self.id2uuid.__reduce__()[1][1]
        data = {"id2uuid": set_id2uuid}
        self.publish('com.cluster.heartbeat', data)

    async def _node_heartbeat_d(self):
        return list(self.id2uuid.items())

    async def _cluster_heartbeat_d(self, data):
        # Node receiving heartbeat update from main
        set_id2uuid = data["id2uuid"]
        self.id2uuid = bidict(set_id2uuid)

    async def _send_heartbeat(self):
        self.id2uuid = await self.call('com.node.update_heartbeat')
        return self.id2uuid

    def setCallback(self, t:str, callback:typing.Callable):
        '''
        Set the message type (string) and a callback function to
        execute when receiving the message of that type.
        '''
        assert(isinstance(t, str))
        self.callback[t] = callback

    async def recv(self, msg):
        self.log.debug('{id} recv: {msg}', id=self.id, msg=msg)
        msgType, data = msg["msgType"], msg["data"]
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        f = self.callback[msgType]
        return await f(data)

    async def send(self, id, msgType, data):
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        msg = { "msgType": msgType,
                "data": data}
        return await self.call(f'com.node{id}.call', msg)

    async def broadcast(self, msgType, data):
        self.log.debug(f'{self.id} broadcast: {data}')
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        msg = { "msgType": msgType,
                "data": data}
        tasks = []
        for id in self.id2uuid.keys():
            if id == self.id:
                continue
            t = self.call(f'com.node{id}.call', msg)
            tasks.append(t)
        return await asyncio.gather(*tasks)