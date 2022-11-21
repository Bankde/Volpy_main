import uuid

global ownerId

class VolObjectRef():
    def __init__(self):
        self.refId: uuid = uuid.uuid4()
        self.owner: uuid = ownerId

    def put(self, val):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def __del__(self):
        raise NotImplementedError

    def done(self, val):
        raise NotImplementedError