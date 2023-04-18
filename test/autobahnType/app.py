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

    async def checkPythonType(self, args) -> str:
        return str(type(args))
    
    async def checkType(self, data):
        t = await self.call("com.js.checkType", data)
        print(f'Data: {data} // {type(data)} // {t}')

    async def runJSCheck(self):
        print("Recv call")
        await self.checkType(123)
        await self.checkType(12.34)
        await self.checkType("t")
        await self.checkType(b"t")
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
Data: b't' // <class 'bytes'> // string
Data: [1, 2, 3] // <class 'list'> // object
Data: {'A': 'B'} // <class 'dict'> // object
"""