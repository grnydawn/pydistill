"""
support for presenting detailed information in failing assertions.
"""
from __future__ import absolute_import, division, print_function

class DummyRewriteHook(object):
    """A no-op import hook for when rewriting is disabled."""

    def mark_rewrite(self, *names):
        pass

