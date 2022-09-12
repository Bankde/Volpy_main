# Conditions:
1. able to save multiple functions' source code (for chained function calls)
2. know the starting function to return at `loads`

# We design the source code pickled, called srcPickled, structure as follows:
1. message["srcs"] = array of string or srcMsg
    string is a source code, or
    srcMsg is an object that's the type as the current message. Used for recursively pack/unpack data.
2. message["obj"] = string of obj name to return the obj at loads 
    set as function name
3. message["modAlias"] = map of module name to alias for importing
    The value can be empty if there is no alias requires. e.g. {"numpy": None}

# Things to consider:
1. order of source code execution?
    Initial test told us that we don't need to care about execution order as long as the function has not been called.
2. able to recursively handle the chain/nested/recursive/closure function
    Should not duplicate the code of nested, closure and recursive function.
3. How to handle module alias in different function scope?
    Separate scope for each `exec` during the deserialization.
4. Then how do we handle shared variables across scope?
    Make sure everything is done within the same pickle process so it can utilizes memoize.
5. reference/value pickle
    Use same logic as cloudpickle

# Things to ignore:
1. modules list - we will test in separate test as it's not need for source code execution


# def loads(m):
#     srcs = m["srcs"]
#     obj = m["obj"]
#     scope = {}
#     for src in srcs:
#         exec(src, scope)
#     return scope[obj]