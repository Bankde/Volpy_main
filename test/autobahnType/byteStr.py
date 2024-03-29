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
        await self.register(self.var1, "com.python.var1")
        await self.register(self.var2, "com.python.var2")
        await self.register(self.var3, "com.python.var3")
        await self.register(self.runJSCheck, "com.python.runJSCheck")
        print("Joined")

    def var1(self, args):
        print("==orig==")
        print(args)
        return [args, str(args), str(type(args))]
    
    def var2(self, args):
        import codecs
        print("==byte==")
        byt = codecs.encode(args, 'utf-8')
        print([c for c in byt])
        return [byt, str(byt), str(type(byt))]

    def var3(self, args):
        import codecs
        print("==byte==")
        byt = codecs.encode(args, 'utf-8')
        b = codecs.decode(byt, 'utf-8', 'backslashreplace')
        print(b)
        print([c for c in b])
        return [b, str(b), str(type(b))]
    
    async def checkType(self, data):
        t = await self.call("com.js.var1", data)
        print(f'Data: {data} // {type(data)}, {t[0]} // {t[1]} // {t[2]} // {type(t[0])}')
        t = await self.call("com.js.var2", data)
        print(f'Data: {data} // {type(data)}, {t[0]} // {t[1]} // {t[2]} // {type(t[0])}')
        t = await self.call("com.js.var3", data)
        print(f'Data: {data} // {type(data)}, {t[0]} // {t[1]} // {t[2]} // {type(t[0])}')

    async def runJSCheck(self):
        print("Run checkJS")
        await self.checkType(b"\x80\x61\x00BC\xff\xee\xddXYZ")
        print("Done checkJS")

if __name__ == "__main__":
    url = "ws://127.0.0.1:8080/ws"
    realm = "Volpy"
    runner = ApplicationRunner(url, realm)
    runner.run(TestWamp)

'''
Run checkJS
Data: b'\x80a\x00BC\xff\xee\xddXYZ' // <class 'bytes'>, b'\x80a\x00BC\xff\xee\xddXYZ' // b'\x80a\x00BC\xff\xee\xddXYZ' // string // <class 'bytes'>
Data: b'\x80a\x00BC\xff\xee\xddXYZ' // <class 'bytes'>, {'0': 0, '1': 103, '2': 71, '3': 69, '4': 65, '5': 81, '6': 107, '7': 80, '8': 47, '9': 55, '10': 116, '11': 49, '12': 89, '13': 87, '14': 86, '15': 111, '16': 61} // 0,103,71,69,65,81,107,80,47,55,116,49,89,87,86,111,61 // object // <class 'dict'>
Data: b'\x80a\x00BC\xff\xee\xddXYZ' // <class 'bytes'>, b'\x80a\x00BC\xff\xee\xddXYZ' // b'\x80a\x00BC\xff\xee\xddXYZ' // string // <class 'bytes'>
Done checkJS

But the JS data is wrong
byteStr.html:33  gGEAQkP/7t1YWVo=
byteStr.html:39 Uint8Array(17) [0, 103, 71, 69, 65, 81, 107, 80, 47, 55, 116, 49, 89, 87, 86, 111, 61, buffer: ArrayBuffer(17), byteLength: 17, byteOffset: 0, length: 17, Symbol(Symbol.toStringTag): 'Uint8Array']
byteStr.html:45  gGEAQkP/7t1YWVo=
'''