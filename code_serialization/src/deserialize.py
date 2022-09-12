import sys
import importlib
import json
import base64

if int(sys.argv[1]) == 0:
    # bytecode
    import cloudpickle as pickleModule
elif int(sys.argv[1]) == 1:
    # srccode
    import codepickle as pickleModule
else:
    exit("Incorrect input")

pickled_file = ".pickled.tmp"
with open(pickled_file) as f:
    pickled_obj = json.load(f)

target_mod_str = (sys.argv[2])[:-3] if (sys.argv[2]).endswith('.py') else None
assert(target_mod_str != None)
target_mod = importlib.import_module(target_mod_str)
assert(target_mod != None)
target_classes = dict([(name, cls) for name, cls in target_mod.__dict__.items() if isinstance(cls, type) and name.startswith('Test')])

for target_class, cls in target_classes.items():
    o = cls()
    pickled = base64.b64decode(pickled_obj[target_class])
    pickled_func = pickleModule.loads(pickled)
    o.testObj(pickled_func)