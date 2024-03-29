import asyncio
from autobahn.asyncio.wamp import ApplicationSession

from bidict import bidict
from addict import Dict as MsgObj
import typing
import logging

'''
crossbar start
# or
docker run -v  $PWD:/node -u 0 --rm --name=crossbar -it -p 8080:8080 crossbario/crossbar
'''

class SimpleWS(ApplicationSession):
    def __init__(self, config):
        ApplicationSession.__init__(self, config)

    def init(self, uuid, is_main=False, logger=logging):
        self.is_main = is_main
        self.id2uuid = bidict()
        self.id2sid = bidict() # sid is session_id (assigned by crossbario)
        self.heartbeatlist = {}
        self.uuid = uuid
        self.id = None
        self.callback = {}
        self.heartbeat = {}
        self.callback["0"] = lambda x: x
        self.dataSendCallback = None
        self.dataRecvCallback = None
        self.logging = logger

    async def onJoin(self, details):
        '''
        Node is subscribing to cluster.heartbeat to update their node online list.
        For the main, no need to subscribe to any node heartbeat, we use wamp.session.on_leave subscription instead.
        '''
        if self.id != None:
            # Already init
            return
        self.logging.info(f'Setup UUID: {self.uuid}')
        if self.is_main:
            await self.register(self._node_register_d, 'com.node.register')
            await self.subscribe(self._node_unregister_d, 'wamp.session.on_leave')
            # Main raylet id should be 0
            self.id = await self._node_register_d(self._session_id, self.uuid)
            await self.register(self.recv, f'com.node{self.id}.call')
            assert(self.id == "0")
            self.logging.info("Setup WS Main Raylet finish")
        else:
            '''
            Subscribe for heartbeat first so when we register the node, 
            we can get heartbeat update right away
            '''
            await self.subscribe(self._cluster_heartbeat_d, 'com.cluster.heartbeat')
            self.id = await self.call('com.node.register', self._session_id, self.uuid)
            await self.register(self.recv, f'com.node{self.id}.call')
            self.logging.info(f'Setup Node finish: sid_{self._session_id} id_{self.id}')

    async def _node_register_d(self, sid, uuid) -> str:
        '''
        Return new node id (str)
        '''
        if uuid in self.id2uuid.inverse:
            id = self.id2uuid.inverse[uuid]
            return id
        else:
            # Generate id for node
            id = str(len(self.id2uuid))
            self.id2uuid[id] = uuid
            self.id2sid[id] = sid
            self.logging.info(f'Reg: {id}, {sid}')
            await self._cluster_update_call()
            return id

    async def _node_unregister_d(self, sid):
        if sid in self.id2sid.inverse:
            id = self.id2sid.inverse[sid]
            self.logging.info(f'Unreg: {id}, {sid}')
            del self.id2uuid[id]
            del self.id2sid[id]
            await self._cluster_update_call()

    async def _cluster_update_call(self):
        set_id2uuid = self.id2uuid.__reduce__()[1][1]
        data = {"id2uuid": set_id2uuid}
        self.publish('com.cluster.heartbeat', data)

    async def _cluster_heartbeat_d(self, data):
        '''
        Node receiving heartbeat update from main.
        '''
        set_id2uuid = data["id2uuid"]
        self.id2uuid = bidict(set_id2uuid)

    def setCallback(self, t, callback:typing.Callable):
        '''
        Set the message type (string) and a callback function to
        execute when receiving the message of that type.
        '''
        self.callback[t] = callback

    async def recv(self, msg):
        self.logging.debug(f'{self.id} recv: {msg}')
        msgType, data = msg["msgType"], msg["data"]
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        data = self.dataRecvCallback(data) if self.dataRecvCallback else data
        f = self.callback[msgType]
        ret_obj = await f(MsgObj(data))
        ret_obj = self.dataSendCallback(ret_obj) if self.dataSendCallback else ret_obj
        return ret_obj

    async def send(self, id: str, msgType, data):
        assert(type(id) == str)
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        data = self.dataSendCallback(data) if self.dataSendCallback else data
        msg = { "msgType": msgType,
                "data": data}
        ret_obj = await self.call(f'com.node{id}.call', msg)
        ret_obj = self.dataRecvCallback(ret_obj) if self.dataRecvCallback else ret_obj
        return MsgObj(ret_obj)

    async def broadcast(self, msgType, data):
        self.logging.debug(f'{self.id} broadcast: {data}')
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        data = self.dataSendCallback(data) if self.dataSendCallback else data
        msg = { "msgType": msgType,
                "data": data}
        tasks = []
        for id in self.id2uuid.keys():
            if id == self.id:
                continue
            t = self.call(f'com.node{id}.call', msg)
            tasks.append(t)
        ts = await asyncio.gather(*tasks)
        if self.dataRecvCallback:
            return [MsgObj(self.dataRecvCallback(t)) for t in ts]
        else:
            return [MsgObj(t) for t in ts]

    def getId(self) -> str:
        return self.id

    def getMainId(self) -> str:
        return "0"