from codepickle.codepickle import *  # noqa
from codepickle.codepickle_fast import CodePickler, dumps, dump, set_config_get_import  # noqa

# Conform to the convention used by python serialization libraries, which
# expose their Pickler subclass at top-level under the  "Pickler" name.
Pickler = CodePickler

__version__ = '2.2.0.dev0'
