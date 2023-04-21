import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

'''
crossbar start
# or
docker run -v  $PWD:/node -u 0 --rm --name=crossbar -it -p 8080:8080 crossbario/crossbar
'''

'''
Testing on byte-str-ArrayBuffer conversion between py-js.
'''

import base64

class TestWamp(ApplicationSession):
    def __init__(self, config):
        ApplicationSession.__init__(self, config)

    async def onJoin(self, details):
        await self.register(self.recv, "com.python.recv")
        await self.register(self.sendFromPythonToJS, "com.python.sendFromPythonToJS")
        print("Joined")

    def recv(self, args):
        print(f"Recv b64: {args}")
        b = base64.b64decode(args)
        print(f"Recv raw: {b}, {type(b)}")
        print(f"Recv byte: {[c for c in b]}")
    
    async def send(self, data):
        print(f"Sending raw: {[c for c in data]}")
        m = base64.b64encode(data)
        m = m.decode('ascii')
        print(f"Sending: {m}")
        await self.call("com.js.recv", m)

    async def sendFromPythonToJS(self):
        await self.send(b"\x80\x61\x00BC\xff\xee\xddXYZ")

if __name__ == "__main__":
    url = "ws://127.0.0.1:8080/ws"
    realm = "Volpy"
    runner = ApplicationRunner(url, realm)
    runner.run(TestWamp)

'''
==== Py2JS ====
Sending raw: [128, 97, 0, 66, 67, 255, 238, 221, 88, 89, 90]
Sending: gGEAQkP/7t1YWVo=

conv.html:33 gGEAQkP/7t1YWVo=
conv.html:39 128,97,0,66,67,255,238,221,88,89,90 object
conv.html:40 Uint8Array(11) [128, 97, 0, 66, 67, 255, 238, 221, 88, 89, 90]

==== JS2Py ====
conv.html:14 Uint8Array(11) [128, 97, 0, 66, 67, 255, 238, 221, 88, 89, 90]
conv.html:20 gGEAQkP/7t1YWVo=

Recv b64: gGEAQkP/7t1YWVo=
Recv raw: b'\x80a\x00BC\xff\xee\xddXYZ', <class 'bytes'>
Recv byte: [128, 97, 0, 66, 67, 255, 238, 221, 88, 89, 90]
'''