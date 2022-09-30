import sys
import importlib
import json
import base64
import helper

if int(sys.argv[1]) == 0:
    # bytecode
    import cloudpickle as pickleModule
elif int(sys.argv[1]) == 1:
    # srccode
    import codepickle as pickleModule
else:
    sys.exit("Incorrect input")

pickled_file = ".pickled.tmp"
open(pickled_file, "w+").close() # Clear the file

pickled_obj = {}

target_mod_str = (sys.argv[2])[:-3] if (sys.argv[2]).endswith('.py') else None
assert(target_mod_str != None)
target_mod = importlib.import_module(target_mod_str)
assert(target_mod != None)
target_classes = dict([(name, cls) for name, cls in target_mod.__dict__.items() if isinstance(cls, type) and name.startswith('Test')])

for target_class, cls in target_classes.items():
    o = cls()
    target_function = o.getFunction()
    bin_obj = pickleModule.dumps(target_function)
    pickled_obj[target_class] = base64.b64encode(bin_obj).decode("utf-8")
    # Test after serialization to prevent alterting of global variables.
    o.testObj(target_function)

with open(pickled_file, 'w') as f:
    json.dump(pickled_obj, f)