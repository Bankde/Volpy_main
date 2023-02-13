from os import environ
import uuid
from .singleton import Singleton

#Python3
class VolpyConfig(object, metaclass=Singleton):
    def __init__(self):
        '''
        The configuration here stores some hard-to-change values.
        Other frequently changed values are handled by argparse and will be merged during runtime.
        '''
        # Main
        self.realm = "Volpy"

        # GRPC
        self.grpc_keepalive_permit_without_calls = 1
        self.grpc_keep_alive = 10000 # ms
        self.grpc_keep_alive_timeout = 2000 # ms

    def merge(self, args):
        # Perform only with argparse, so there shouldn't be any pollution here.
        args_dict = vars(args)
        for k,v in args_dict.items():
            setattr(self, k, v)

config = VolpyConfig()
