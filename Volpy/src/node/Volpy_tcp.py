from os import environ
import asyncio
from autobahn.wamp.types import ComponentConfig
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

import uuid
import time
from bidict import bidict

IS_MAIN = bool(environ.get("VOLPY_TCP_MAIN", False))
ROUTER_URL = environ.get("VOLPY_ROUTER", "ws://127.0.0.1:8080/ws")
REALM = "Volpy"
volpy_tcp = None

class VolpyTCP(ApplicationSession):
    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.init()

    def init(self):
        self.id2uuid = bidict()
        self.id2sid = bidict()
        self.uuid = str(uuid.uuid4())
        self.log.info('Setup UUID: {uuid}', uuid=self.uuid)
        self.id = None
        self.callback = {}
        self.heartbeat = {}
        self.callback["0"] = lambda x: x

    async def onJoin(self, details):
        if self.id:
            # Already init
            return
        if IS_MAIN:
            await self.register(self._node_register_d, 'com.cluster.register')
            await self.subscribe(self._node_unregister_d, 'wamp.session.on_leave')
            await self.register(self._node_sync_d, 'com.cluster.syncinfo')
            self.log.info("Setup Main finish")
        else:
            '''
            Subscribe for heartbeat first so 
            when we register the node, 
            we can get heartbeat update right away
            '''
            await self.subscribe(self._cluster_update_d, 'com.cluster.updateinfo')
            self.id = await self.call('com.cluster.register', self._session_id, self.uuid)
            await self.register(self.recv, f'com.node{self.id}.exec')
            self.log.info(f'Setup Node finish: sid_{self._session_id} id_{self.id}')

    async def _print_session_d(self, data):
        print(data)

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
        self.publish('com.cluster.updateinfo', data)

    async def _node_sync_d(self):
        return list(self.id2uuid.items())

    async def _cluster_update_d(self, data):
        # Node receiving update from heartbeat (published from main)
        self.log.info(f'Setup UUID: {self.uuid}')
        set_id2uuid = data["id2uuid"]
        self.id2uuid = bidict(set_id2uuid)

    async def sync_nodeid_list(self):
        self.id2uuid = await self.call('com.cluster.syncinfo')
        return self.id2uuid

    async def get_nodeid_list(self):
        return list(self.id2uuid.keys())

    def setCallback(self, t, callback):
        self.callback[t] = callback

    async def recv(self, msg):
        print(f'{self.id} recv: {msg}')
        # self.log.info(f'{self.id} recv: {msg}')
        msgType, data = msg["msgType"], msg["data"]
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        f = self.callback[msgType]
        f(data)
        return "Hi"

    async def send(self, id, msgType, data):
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        msg = { "msgType": msgType,
                "data": data}
        return await self.call(f'com.node{id}.exec', msg)

    async def broadcast(self, msgType, data):
        self.log.info(f'{self.id} broadcast: {data}')
        if msgType not in self.callback:
            raise RuntimeError("MsgType not implemented")
        msg = { "msgType": msgType,
                "data": data}
        tasks = []
        for id in self.id2uuid.keys():
            if id == self.id:
                continue
            self.log.debug(f"{self.id} send: {id}, {msg}")
            t = self.call(f'com.node{id}.exec', msg)
            tasks.append(t)
        return await asyncio.gather(*tasks)

from ptpython.repl import embed, run_config, PythonRepl
def default_configure(repl: PythonRepl):
    """
    Default REPL configuration function
    :param repl:
    :return:
    """
    repl.show_signature = True
    repl.show_docstring = True
    repl.show_status_bar = True
    repl.show_sidebar_help = True
    repl.highlight_matching_parenthesis = True
    repl.wrap_lines = True
    repl.complete_while_typing = True
    repl.vi_mode = False
    repl.paste_mode = False
    repl.prompt_style = 'classic'  # 'classic' or 'ipython'
    repl.insert_blank_line_after_output = False
    repl.enable_history_search = False
    repl.enable_auto_suggest = False
    repl.enable_open_in_editor = True
    repl.enable_system_bindings = False
    repl.confirm_exit = True
    repl.enable_input_validation = True

async def start_repl(loop, session):
    configure = default_configure
    await embed(
        globals={},
        locals={"session": session},
        title='AutoBahn-Python REPL',
        return_asyncio_coroutine=True,
        patch_stdout=True,
        configure=configure
    )

if __name__ == '__main__':
    session = VolpyTCP(ComponentConfig(REALM, {}))
    runner = ApplicationRunner(ROUTER_URL, REALM)
    if IS_MAIN:
        runner.run(session, start_loop=True, log_level='info')
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.ensure_future(runner.run(session, start_loop=False, log_level='info'), loop=loop)
        loop.run_until_complete(start_repl(loop, session))
        loop.stop()