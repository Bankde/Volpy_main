registerRemote = None
put = None
get = None
VolpyDataRef_class = None

def VolpyDataRef(kwargs):
    global VolpyDataRef_class
    return VolpyDataRef_class(kwargs)

def setup(dep):
    global registerRemote, put, get, VolpyDataRef_class
    registerRemote = dep.registerRemote
    put = dep.put
    get = dep.get
    VolpyDataRef_class = dep.VolpyDataRef