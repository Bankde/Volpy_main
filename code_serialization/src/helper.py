# ------------------
# Cloudpickle finder
# ------------------
import sys, weakref, dis, types, opcode, itertools

# relevant opcodes
STORE_GLOBAL = opcode.opmap['STORE_GLOBAL']
DELETE_GLOBAL = opcode.opmap['DELETE_GLOBAL']
LOAD_GLOBAL = opcode.opmap['LOAD_GLOBAL']
GLOBAL_OPS = (STORE_GLOBAL, DELETE_GLOBAL, LOAD_GLOBAL)
HAVE_ARGUMENT = dis.HAVE_ARGUMENT
EXTENDED_ARG = dis.EXTENDED_ARG

# COLLECTION OF OBJECTS STATE GETTERS
# -----------------------------------
def _function_getstate(func):
    # - Put func's dynamic attributes (stored in func.__dict__) in state. These
    #   attributes will be restored at unpickling time using
    #   f.__dict__.update(state)
    # - Put func's members into slotstate. Such attributes will be restored at
    #   unpickling time by iterating over slotstate and calling setattr(func,
    #   slotname, slotvalue)
    slotstate = {
        "__name__": func.__name__,
        "__qualname__": func.__qualname__,
        "__annotations__": func.__annotations__,
        "__kwdefaults__": func.__kwdefaults__,
        "__defaults__": func.__defaults__,
        "__module__": func.__module__,
        "__doc__": func.__doc__,
        "__closure__": func.__closure__,
    }

    f_globals_ref = _extract_code_globals(func.__code__)
    f_globals = {k: func.__globals__[k] for k in f_globals_ref if k in
                 func.__globals__}

    closure_values = (
        list(map(_get_cell_contents, func.__closure__))
        if func.__closure__ is not None else ()
    )

    # Extract currently-imported submodules used by func. Storing these modules
    # in a smoke _cloudpickle_subimports attribute of the object's state will
    # trigger the side effect of importing these modules at unpickling time
    # (which is necessary for func to work correctly once depickled)
    slotstate["_cloudpickle_submodules"] = _find_imported_submodules(
        func.__code__, itertools.chain(f_globals.values(), closure_values))
    slotstate["__globals__"] = f_globals

    state = func.__dict__
    return state, slotstate

_extract_code_globals_cache = weakref.WeakKeyDictionary()

def _extract_code_globals(co):
    """
    Find all globals names read or written to by codeblock co
    """
    out_names = _extract_code_globals_cache.get(co)
    if out_names is None:
        # We use a dict with None values instead of a set to get a
        # deterministic order (assuming Python 3.6+) and avoid introducing
        # non-deterministic pickle bytes as a results.
        out_names = {name: None for name in _walk_global_ops(co)}

        # Declaring a function inside another one using the "def ..."
        # syntax generates a constant code object corresponding to the one
        # of the nested function's As the nested function may itself need
        # global variables, we need to introspect its code, extract its
        # globals, (look for code object in it's co_consts attribute..) and
        # add the result to code_globals
        if co.co_consts:
            for const in co.co_consts:
                if isinstance(const, types.CodeType):
                    out_names.update(_extract_code_globals(const))

        _extract_code_globals_cache[co] = out_names

    return out_names

def _walk_global_ops(code):
    """
    Yield referenced name for all global-referencing instructions in *code*.
    """
    for instr in dis.get_instructions(code):
        op = instr.opcode
        if op in GLOBAL_OPS:
            yield instr.argval
            
def _get_cell_contents(cell):
    try:
        return cell.cell_contents
    except ValueError:
        # sentinel used by ``_fill_function`` which will leave the cell empty
        return _empty_cell_value
    
def _find_imported_submodules(code, top_level_dependencies):
    """
    Find currently imported submodules used by a function.

    Submodules used by a function need to be detected and referenced for the
    function to work correctly at depickling time. Because submodules can be
    referenced as attribute of their parent package (``package.submodule``), we
    need a special introspection technique that does not rely on GLOBAL-related
    opcodes to find references of them in a code object.

    Example:
    ```
    import concurrent.futures
    import cloudpickle
    def func():
        x = concurrent.futures.ThreadPoolExecutor
    if __name__ == '__main__':
        cloudpickle.dumps(func)
    ```
    The globals extracted by cloudpickle in the function's state include the
    concurrent package, but not its submodule (here, concurrent.futures), which
    is the module used by func. Find_imported_submodules will detect the usage
    of concurrent.futures. Saving this module alongside with func will ensure
    that calling func once depickled does not fail due to concurrent.futures
    not being imported
    """

    subimports = []
    # check if any known dependency is an imported package
    for x in top_level_dependencies:
        if (isinstance(x, types.ModuleType) and
                hasattr(x, '__package__') and x.__package__):
            # check if the package has any currently loaded sub-imports
            prefix = x.__name__ + '.'
            # A concurrent thread could mutate sys.modules,
            # make sure we iterate over a copy to avoid exceptions
            for name in list(sys.modules):
                # Older versions of pytest will add a "None" module to
                # sys.modules.
                if name is not None and name.startswith(prefix):
                    # check whether the function can address the sub-module
                    tokens = set(name[len(prefix):].split('.'))
                    if not tokens - set(code.co_names):
                        subimports.append(sys.modules[name])
    return subimports

# ------------------
# pyodide finder
# ------------------

import ast
from textwrap import dedent

def find_imports(source: str) -> list[str]:
    """
    Finds the imports in a Python source code string
    Parameters
    ----------
    source : str
       The Python source code to inspect for imports.
    Returns
    -------
    ``List[str]``
        A list of module names that are imported in ``source``. If ``source`` is not
        syntactically correct Python code (after dedenting), returns an empty list.
    Examples
    --------
    >>> from pyodide import find_imports
    >>> source = "import numpy as np; import scipy.stats"
    >>> find_imports(source)
    ['numpy', 'scipy']
    """
    # handle mis-indented input from multi-line strings
    source = dedent(source)

    try:
        mod = ast.parse(source)
    except SyntaxError:
        return []
    imports = set()
    for node in ast.walk(mod):
        if isinstance(node, ast.Import):
            for name in node.names:
                node_name = name.name
                imports.add(node_name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            if module_name is None:
                continue
            imports.add(module_name.split(".")[0])
    return list(sorted(imports))