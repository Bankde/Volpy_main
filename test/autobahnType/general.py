import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

'''
crossbar start
# or
docker run -v  $PWD:/node -u 0 --rm --name=crossbar -it -p 8080:8080 crossbario/crossbar
'''

class TestWamp(ApplicationSession):
    def __init__(self, config):
        ApplicationSession.__init__(self, config)

    async def onJoin(self, details):
        await self.register(self.checkPythonType, "com.python.checkType")
        await self.register(self.runJSCheck, "com.python.runJSCheck")
        print("Joined")

    def checkPythonType(self, args) -> str:
        # import codecs
        # if isinstance(args, str):
        #     print("==str==")
        #     print([c for c in args])
        #     print("==byte==")
        #     a = codecs.encode(args, 'utf-8')
        #     print([c for c in args])
        #     print("==str==")
        #     b = codecs.decode(a, 'utf-8', 'backslashreplace')
        #     print(b)
        #     print([c for c in b])
        return str(type(args))
    
    async def checkType(self, data):
        t = await self.call("com.js.checkType", data)
        print(f'Data: {data} // {type(data)} // {t}')

    async def runJSCheck(self):
        print("Recv call")
        await self.checkType(123)
        await self.checkType(12.34)
        await self.checkType("t")
        await self.checkType(b"\x80\x61\x00BC\xff\xee\xddXYZ")
        await self.checkType([1,2,3])
        await self.checkType({"A":"B"})

if __name__ == "__main__":
    url = "ws://127.0.0.1:8080/ws"
    realm = "Volpy"
    runner = ApplicationRunner(url, realm)
    runner.run(TestWamp)

"""
Data: 123 // <class 'int'> // number
Data: 12.34 // <class 'float'> // number
Data: t // <class 'str'> // string
Data: b'\x80a\x00BC\xff\xee\xddXYZ' // <class 'bytes'> // string
Data: [1, 2, 3] // <class 'list'> // object
Data: {'A': 'B'} // <class 'dict'> // object

Uint8Array [116, buffer: ArrayBuffer(1), byteLength: 1, byteOffset: 0, length: 1, Symbol(Symbol.toStringTag): 'Uint8Array']0: 116buffer: ArrayBuffer(1)byteLength: 1maxByteLength: 1resizable: false[[Prototype]]: ArrayBuffer[[Int8Array]]: Int8Array(1)[[Uint8Array]]: Uint8Array(1)[[ArrayBufferByteLength]]: 1[[ArrayBufferData]]: 436byteLength: 1byteOffset: 0length: 1Symbol(Symbol.toStringTag): "Uint8Array"[[Prototype]]: TypedArray
(index):28  gGEAQkP/7t1YWVo=
(index):31 Uint8Array(17) [0, 103, 71, 69, 65, 81, 107, 80, 47, 55, 116, 49, 89, 87, 86, 111, 61, buffer: ArrayBuffer(17), byteLength: 17, byteOffset: 0, length: 17, Symbol(Symbol.toStringTag): 'Uint8Array']
"""