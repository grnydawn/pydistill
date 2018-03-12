""" hook specifications for pydistill plugins, invoked from main.py and builtin plugins.  """

from pluggy import HookspecMarker

hookspec = HookspecMarker("pydistill")

# -------------------------------------------------------------------------
# Initialization hooks called for every plugin
# -------------------------------------------------------------------------


@hookspec(historic=True)
def pydistill_addhooks(pluginmanager):
    """called at plugin registration time to allow adding new hooks via a call to
    ``pluginmanager.add_hookspecs(module_or_class, prefix)``.


    :param _pydistill.config.PyDistillPluginManager pluginmanager: pydistill plugin manager

    .. note::
        This hook is incompatible with ``hookwrapper=True``.
    """

@hookspec(historic=True)
def pydistill_namespace():
    """
    (**Deprecated**) this hook causes direct monkeypatching on pydistill, its use is strongly discouraged
    return dict of name->object to be made globally available in
    the pydistill namespace.

    This hook is called at plugin registration time.

    .. note::
        This hook is incompatible with ``hookwrapper=True``.
    """


@hookspec(historic=True)
def pydistill_plugin_registered(plugin, manager):
    """ a new pydistill plugin got registered.

    :param plugin: the plugin module or instance
    :param _pydistill.config.PyDistillPluginManager manager: pydistill plugin manager

    .. note::
        This hook is incompatible with ``hookwrapper=True``.
    """

@hookspec(historic=True)
def pydistill_addoption(parser):
    """register argparse-style options and ini-style config values,
    called once at the beginning of a test run.

    .. note::

        This function should be implemented only in plugins or ``conftest.py``
        files situated at the tests root directory due to how pydistill
        :ref:`discovers plugins during startup <pluginorder>`.

    :arg _pydistill.config.Parser parser: To add command line options, call
        :py:func:`parser.addoption(...) <_pydistill.config.Parser.addoption>`.
        To add ini-file values call :py:func:`parser.addini(...)
        <_pydistill.config.Parser.addini>`.

    Options can later be accessed through the
    :py:class:`config <_pydistill.config.Config>` object, respectively:

    - :py:func:`config.getoption(name) <_pydistill.config.Config.getoption>` to
      retrieve the value of a command line option.

    - :py:func:`config.getini(name) <_pydistill.config.Config.getini>` to retrieve
      a value read from an ini-style file.

    The config object is passed around on many internal objects via the ``.config``
    attribute or can be retrieved as the ``pydistillconfig`` fixture.

    .. note::
        This hook is incompatible with ``hookwrapper=True``.
    """


@hookspec(historic=True)
def pydistill_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.

    This hook is called for every plugin and initial conftest file
    after command line options have been parsed.

    After that, the hook is called for other conftest files as they are
    imported.

    .. note::
        This hook is incompatible with ``hookwrapper=True``.

    :arg _pydistill.config.Config config: pydistill config object
    """

# -------------------------------------------------------------------------
# Bootstrapping hooks called for plugins registered early enough:
# internal and 3rd party plugins.
# -------------------------------------------------------------------------


@hookspec(firstresult=True)
def pydistill_cmdline_parse(pluginmanager, args):
    """return initialized config object, parsing the specified args.

    Stops at first non-None result, see :ref:`firstresult`

    .. note::
        This hook will not be called for ``confextract.py`` files, only for setuptools plugins.

    :param _pydistill.config.PyDistillPluginManager pluginmanager: pydistill plugin manager
    :param list[str] args: list of arguments passed on the command line
    """


@hookspec(firstresult=True)
def pydistill_cmdline_main(config):
    """ called for performing the main command line action. The default
    implementation will invoke the configure hooks and runtest_mainloop.

    .. note::
        This hook will not be called for ``confextract.py`` files, only for setuptools plugins.

    Stops at first non-None result, see :ref:`firstresult`

    :param _pydistill.config.Config config: pydistill config object
    """


def pydistill_load_initial_conftests(early_config, parser, args):
    """ implements the loading of initial conftest files ahead
    of command line option parsing.

    .. note::
        This hook will not be called for ``confextract.py`` files, only for setuptools plugins.

    :param _pydistill.config.Config early_config: pydistill config object
    :param list[str] args: list of arguments passed on the command line
    :param _pydistill.config.Parser parser: to add command line options
    """

