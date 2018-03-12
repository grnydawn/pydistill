"""
This module contains deprecation messages and bits of code used elsewhere in the codebase
that is planned to be removed in the next pydistill release.

Keeping it in a central location makes it easy to track what is deprecated and should
be removed when the time comes.
"""
from __future__ import absolute_import, division, print_function


class RemovedInPytest4Warning(DeprecationWarning):
    """warning class for features removed in pydistill X.X"""

TEST_WARNING = 'This is a test warning message.'
