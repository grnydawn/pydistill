# PYTHON_ARGCOMPLETE_OK
"""
pydistill: Automated data distillation tool.
"""


# else we are imported

from _pydistill.config import (
    main, UsageError, cmdline,
    exthookspec, exthookimpl,
    langhookspec, langhookimpl
)

#from _pydistill.fixtures import fixture, yield_fixture
#from _pydistill.assertion import register_assert_rewrite
#from _pydistill.freeze_support import freeze_includes
from _pydistill import __version__
#from _pydistill.debugging import pydistillPDB as __pydistillPDB
#from _pydistill.recwarn import warns, deprecated_call
#from _pydistill.outcomes import fail, skip, importorskip, exit, xfail
#from _pydistill.mark import MARK_GEN as mark, param
#from _pydistill.main import Session
#from _pydistill.nodes import Item, Collector, File
#from _pydistill.fixtures import fillfixtures as _fillfuncargs
#from _pydistill.python import (
#    Module, Class, Instance, Function, Generator,
#)

#from _pydistill.python_api import approx, raises

#set_trace = __pydistillPDB.set_trace

__all__ = [
    'main',
    'UsageError',
    'cmdline',
    'exthookspec',
    'exthookimpl',
    'langhookspec',
    'langhookimpl',
    '__version__',
#    'register_assert_rewrite',
#    'freeze_includes',
#    'set_trace',
#    'warns',
#    'deprecated_call',
#    'fixture',
#    'yield_fixture',
#    'fail',
#    'skip',
#    'xfail',
#    'importorskip',
#    'exit',
#    'mark',
#    'param',
#    'approx',
#    '_fillfuncargs',
#
#    'Item',
#    'File',
#    'Collector',
#    'Session',
#    'Module',
#    'Class',
#    'Instance',
#    'Function',
#    'Generator',
#    'raises',


]

if __name__ == '__main__':
    # if run as a script or by 'python -m pydistill'
    # we trigger the below "else" condition by the following import
    import pydistill
    raise SystemExit(pydistill.main())
else:
    pass
    #from _pydistill.compat import _setup_collect_fakemodule
    #_setup_collect_fakemodule()
