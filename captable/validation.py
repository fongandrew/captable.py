"""Validators are callables that can be run on a table state to make sure
things are copacetic. By default, the DEFAULT_VALIDATORS will be run after
each transaction during CapTable processing.

Validators are not intended to be the *sole* source of ensuring cap table
correctness. Transactions may do some validation themselves and may refuse to 
process or process differently if things don't check out.
"""
from __future__ import absolute_import
from .securities import Security

def check_auth(state):
    """Check the SecuritiesState and makes sure amounts add up"""
    for name, metastate in state.get(Security.STATE_KEY, {}).iteritems():
        if hasattr(metastate, "authorized") and hasattr(metastate, "issued"):
            assert metastate.authorized >= metastate.issued, (
                name + " Warning: " + metastate.issued + 
                " issued but only " + metastate.authorized + " authorized"
            )

DEFAULT_VALIDATORS = [check_auth]