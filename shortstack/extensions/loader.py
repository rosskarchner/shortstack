import inspect
import warnings
import os
import sys

from importlib import import_module
from pkg_resources import iter_entry_points

from .api import Extension

sys.path.append(os.getcwd())


available_extensions = {}

for ext_mod in iter_entry_points(group='shortstack_ext', name=None):
    available_extensions[ext_mod.name] = ext_mod

def extensions_from_module(mod):
    mod_ns = inspect.getmembers(mod)
    extensions = [obj for name, obj in mod_ns if type(obj) == Extension]
    return extensions


def extensions_from_name(name):
    if name == '':
        return []
    try:
        mod = available_extensions.get(name).load()
        return extensions_from_module(mod)
    except ImportError:
        warnings.warn("could not load extension '%s', but continuing" % name)
        return []


def load_extensions(extension_names):
    if extension_names:
        extensions_nested = map(extensions_from_name, extension_names)
        # fastest way to flatten nested lists, per Alex Martelli
        # http://stackoverflow.com/a/952952
        return [item for sublist in extensions_nested for item in sublist]
    else:
        return []
