import os
import errno
from .singleton import Singleton
from enum import Enum

class Status(Enum):
    SUCCESS = 0
    EXECUTION_ERROR = 1
    SERIALIZATION_ERROR = 2
    DATA_NOT_FOUND = 3
    DATA_ON_OTHER = 4

class Counter(object, metaclass=Singleton):
    '''
    Singleton counter for id/logging/debugging
    '''
    def __init__(self):
        self.count = 0

    def getCount(self):
        c = self.count
        self.count += 1
        return c

counter = Counter()

def pid_exists(pid):
    if pid == 0:
        return True
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
        elif err.errno == errno.EPERM:
            return True
        else:
            raise err
    else:
        return True
    
def generateDataRef():
    return str(uuid.uuid4())