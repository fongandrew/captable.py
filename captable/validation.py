"""Validators are callables that can be run on a table state to make sure
things are copacetic. By default, the DEFAULT_VALIDATORS will be run after
each transaction during CapTable processing.

Validators are not intended to be the *sole* source of ensuring cap table
correctness. Transactions may do some validation themselves and may refuse to 
process or process differently if things don't check out.
"""
from __future__ import absolute_import

from .state import SecuritiesState

def check_amounts(state):
    """Check the SecuritiesState and makes sure amounts add up"""
    if state.securities:
        for cls, amounts in state.securities.iteritems():
            if (amounts.authorized < amounts.issued):
                msg = (cls.name + " Warning: " + amounts.issued + 
                       " issued but only " + amounts.authorized + " authorized")
                state.warn(msg)
            elif (amounts.issued < amounts.outstanding):
                msg = (cls.name + " Warning: " + amounts.outstanding + 
                       " outstanding but only " + amounts.issued + " issued")
                state.warn(msg)

DEFAULT_VALIDATORS = [check_amounts]