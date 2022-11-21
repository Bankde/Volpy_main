

class VolMetatable():
    dict = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(VolMetatable, cls).__new__(cls)
        return cls.instance

    def insert(self, )