""" command line options, ini-file and conftest.py processing. """
from __future__ import absolute_import, division, print_function
import argparse
import shlex
import traceback
import types
import warnings

import six
import py
# DON't import pydistill here because it causes import cycle troubles
import sys
import os
import _pydistill.exthookspec  # the extension definitions
import _pydistill.langhookspec  # the language definitions
import _pydistill.assertion
from pluggy import PluginManager, HookimplMarker, HookspecMarker

# pydistill extension plugins
exthookspec = HookspecMarker("pydistill")
exthookimpl = HookimplMarker("pydistill")

# pydistill language plugins
langhookspec = HookspecMarker("pydistill_lang")
langhookimpl = HookimplMarker("pydistill_lang")

# pydistill startup
#

class ConfextractImportFailure(Exception):
    def __init__(self, path, excinfo):
        Exception.__init__(self, path, excinfo)
        self.path = path
        self.excinfo = excinfo

    def __str__(self):
        etype, evalue, etb = self.excinfo
        formatted = traceback.format_tb(etb)
        # The level of the tracebacks we want to print is hand crafted :(
        return repr(evalue) + '\n' + ''.join(formatted[2:])


def main(args=None, plugins=None):
    """ return exit code, after performing an in-process test run.

    :arg args: list of command line arguments.

    :arg plugins: list of plugin objects to be auto-registered during
                  initialization.
    """
    try:
        try:
            config = _prepareconfig(args, plugins)
        except ConfextractImportFailure as e:
            tw = py.io.TerminalWriter(sys.stderr)
            for line in traceback.format_exception(*e.excinfo):
                tw.line(line.rstrip(), red=True)
            tw.line("ERROR: could not load %s\n" % (e.path), red=True)
            return 4
        else:
            try:
                return config.hook.pydistill_cmdline_main(config=config)
            finally:
                config._ensure_unconfigure()
    except UsageError as e:
        tw = py.io.TerminalWriter(sys.stderr)
        for msg in e.args:
            tw.line("ERROR: {}\n".format(msg), red=True)
        return 4


class cmdline(object):  # compatibility namespace
    main = staticmethod(main)

class UsageError(Exception):
    """ error in pydistill usage or invocation"""

default_plugins = ( "csv" )

builtin_plugins = set(default_plugins)
#builtin_plugins.add("pytester")


def get_config(subcmd):
    # subsequent calls to main will create a fresh instance
    pluginmanager = PyDistillPluginManager()
    config = Config(pluginmanager)
    for spec in default_plugins:
        #pluginmanager.import_plugin(spec)
        if spec == subcmd:
            pluginmanager.import_plugin(spec)
    return config

def _prepareconfig(args=None, plugins=None):
    warning = None
    if args is None:
        subcmd = sys.argv[1] if len(sys.argv) > 1 else None
        args = sys.argv[2:] if len(sys.argv) > 2 else []
    elif isinstance(args, py.path.local):
        subcmd = "macro"
        args = [str(args)]
    elif not isinstance(args, (tuple, list)):
        if not isinstance(args, str):
            raise ValueError("not a string or argument list: %r" % (args,))
        _args = shlex.split(args, posix=sys.platform != "win32")
        subcmd = _args[0] if len(_args) > 0 else None
        args = _args[1:] if len(_args) > 1 else []
        from _pydistill import deprecated
        warning = deprecated.TEST_WARNING
    config = get_config(subcmd)
    pluginmanager = config.pluginmanager
    try:
        if plugins:
            for plugin in plugins:
                if isinstance(plugin, six.string_types):
                    pluginmanager.consider_pluginarg(plugin)
                else:
                    pluginmanager.register(plugin)
        if warning:
            config.warn('C1', warning)
        return pluginmanager.hook.pydistill_cmdline_parse(
            pluginmanager=pluginmanager, subcmd=subcmd, args=args)
    except BaseException:
        config._ensure_unconfigure()
        raise

class PyDistillPluginManager(PluginManager):
    """
    Overwrites :py:class:`pluggy.PluginManager <pluggy.PluginManager>` to add pydistill-specific
    functionality:

    * loading plugins from the command line, ``PYDISTILL_PLUGIN`` env variable and
      ``pydistill_plugins`` global variables found in plugins being loaded;
    * ``confdistill.py`` loading during start-up;
    """

    def __init__(self):
        super(PyDistillPluginManager, self).__init__("pydistill", implprefix="pydistill_")
        self._confdistill_plugins = set()

        # state related to local conftest plugins
        self._path2confmods = {}
        self._confdistillpath2mod = {}
        self._confcutdir = None
        self._noconfdistill = False
        self._duplicatepaths = set()

        self.add_hookspecs(_pydistill.exthookspec)
        self.register(self)
        if os.environ.get('PYDISTILL_DEBUG'):
            err = sys.stderr
            encoding = getattr(err, 'encoding', 'utf8')
            try:
                err = py.io.dupfile(err, encoding=encoding)
            except Exception:
                pass
            self.trace.root.setwriter(err.write)
            self.enable_tracing()

        # Config._consider_importhook will set a real object if required.
        self.rewrite_hook = _pydistill.assertion.DummyRewriteHook()

    def _warn(self, message):
        kwargs = message if isinstance(message, dict) else {
            'code': 'I1',
            'message': message,
            'fslocation': None,
            'nodeid': None,
        }
        self.hook.pydistill_logwarning.call_historic(kwargs=kwargs)

class Parser(object):
    """ Parser for command line arguments and ini-file values.

    :ivar extra_info: dict of generic param -> value to display in case
        there's an error processing the command line arguments.
    """

    def __init__(self, usage=None, processopt=None):
        self._anonymous = OptionGroup("custom options", parser=self)
        self._groups = []
        self._processopt = processopt
        self._usage = usage
        self._inidict = {}
        self._ininames = []
        self.extra_info = {}


    def parse_known_and_unknown_args(self, subcmd, args, namespace=None):
        """parses and returns a namespace object with known arguments, and
        the remaining arguments unknown at this point.
        """
        optparser = self._getparser(subcmd)
        args = [str(x) for x in args]
        return optparser.parse_known_args(subcmd, args, namespace=namespace)

    def _getparser(self, subcmd):
        #TODO: get groups from installed plugins. remove unnecessary subcmd argument
        #TODO: Hierachcial Plugins with Language classification
        #TODO: Mgr -> KGenMgr
        #TODO: HookSpec -> IOHookSpec -> (ReadHookSpec, WriterHookSpec)
        from _pydistill._argcomplete import filescompleter
        optparser = MyOptionParser(self, self.extra_info)
        groups = self._groups + [self._anonymous]
        for group in groups:
            if group.options:
                desc = group.description or group.name
                arggroup = optparser.add_argument_group(desc)
                for option in group.options:
                    n = option.names()
                    a = option.attrs()
                    arggroup.add_argument(*n, **a)
        # bash like autocompletion for dirs (appending '/')
        optparser.add_argument(FILE_OR_DIR, nargs='*').completer = filescompleter
        return optparser

class OptionGroup(object):
    def __init__(self, name, description="", parser=None):
        self.name = name
        self.description = description
        self.options = []
        self.parser = parser

class CmdOptions(object):
    """ holds cmdline options as attributes."""

    def __init__(self, values=()):
        self.__dict__.update(values)

    def __repr__(self):
        return "<CmdOptions %r>" % (self.__dict__,)

    def copy(self):
        return CmdOptions(self.__dict__)

class Config(object):
    """ access to configuration values, pluginmanager and plugin hooks.  """

    def __init__(self, pluginmanager):
        #: access to command line option as attributes.
        #: (deprecated), use :py:func:`getoption() <_pytest.config.Config.getoption>` instead
        self.option = CmdOptions()
        self._parser = Parser(
            usage="%%(prog)s sub-command [options] source-file",
            processopt=self._processopt,
        )
        #: a pluginmanager instance
        self.pluginmanager = pluginmanager
        self.trace = self.pluginmanager.trace.root.get("config")
        self.hook = self.pluginmanager.hook
        self._inicache = {}
        self._override_ini = ()
        self._opt2dest = {}
        self._cleanup = []
        self._warn = self.pluginmanager._warn
        self.pluginmanager.register(self, "pydistillconfig")
        self._configured = False

        def do_setns(dic):
            import pydistill
            setns(pydistill, dic)

        self.hook.pydistill_namespace.call_historic(do_setns, {})
        self.hook.pydistill_addoption.call_historic(kwargs=dict(parser=self._parser))

    def _processopt(self, opt):
        for name in opt._short_opts + opt._long_opts:
            self._opt2dest[name] = opt.dest

        if hasattr(opt, 'default') and opt.dest:
            if not hasattr(self.option, opt.dest):
                setattr(self.option, opt.dest, opt.default)

    def _initini(self, subcmd, args):
        ns, unknown_args = self._parser.parse_known_and_unknown_args(subcmd, args, namespace=self.option.copy())
        r = determine_setup(ns.inifilename, ns.file_or_dir + unknown_args, warnfunc=self.warn)
        self.rootdir, self.inifile, self.inicfg = r
        self._parser.extra_info['rootdir'] = self.rootdir
        self._parser.extra_info['inifile'] = self.inifile
        self.invocation_dir = py.path.local()
        self._parser.addini('addopts', 'extra command line options', 'args')
        self._parser.addini('minversion', 'minimally required pytest version')
        self._override_ini = ns.override_ini or ()

    def _ensure_unconfigure(self):
        if self._configured:
            self._configured = False
            self.hook.pydistill_unconfigure(config=self)
            self.hook.pydistill_configure._call_history = []
        while self._cleanup:
            fin = self._cleanup.pop()
            fin()

    def pydistill_cmdline_parse(self, pluginmanager, subcmd, args):
        # REF1 assert self == pluginmanager.config, (self, pluginmanager.config)
        self.parse(subcmd, args)
        return self

    def _preparse(self, subcmd, args, addopts=True):
        if addopts:
            args[:] = shlex.split(os.environ.get('PYDISTILL_ADDOPTS', '')) + args
        self._initini(subcmd, args)
        if addopts:
            args[:] = self.getini("addopts") + args
        self._checkversion()
        self._consider_importhook(subcmd, args)
        self.pluginmanager.consider_preparse(subcmd, args)
        self.pluginmanager.load_setuptools_entrypoints('pydistill11')
        self.pluginmanager.consider_env()
        self.known_args_namespace = ns = self._parser.parse_known_args(subcmd, args, namespace=self.option.copy())
        if self.known_args_namespace.confcutdir is None and self.inifile:
            confcutdir = py.path.local(self.inifile).dirname
            self.known_args_namespace.confcutdir = confcutdir
        try:
            self.hook.pydistill_load_initial_conftests(early_config=self,
                                                    subcmd=subcmd, args=args, parser=self._parser)
        except ConfextractImportFailure:
            e = sys.exc_info()[1]
            if ns.help or ns.version:
                # we don't want to prevent --help/--version to work
                # so just let is pass and print a warning at the end
                self._warn("could not load initial conftests (%s)\n" % e.path)
            else:
                raise

    def parse(self, subcmd, args, addopts=True):
        # parse given cmdline arguments into this config object.
        assert not hasattr(self, 'subcmd'), (
            "can only parse cmdline args at most once per Config object")
        self._origargs = args
        self.hook.pydistill_addhooks.call_historic(
            kwargs=dict(pluginmanager=self.pluginmanager))
        self._preparse(subcmd, args, addopts=addopts)
        # XXX deprecated hook:
        self.hook.pydistill_cmdline_preparse(config=self, subcmd=subcmd, args=args)
        self._parser.after_preparse = True
        try:
            subcmd, args = self._parser.parse_setoption(subcmd, args, self.option, namespace=self.option)
            if not args:
                cwd = os.getcwd()
                if cwd == self.rootdir:
                    args = self.getini('testpaths')
                if not args:
                    args = [cwd]
            self.subcmd = subcmd
            self.args = args
        except PrintHelp:
            pass

