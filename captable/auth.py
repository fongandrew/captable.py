"""Transactions represent some modification of or addition to a captable
at some point in time.
"""
from __future__ import absolute_import

import datetime
from . import securities
from . import state


class AuthTransaction(object):
    """Transaction authorizing a new security

    Args:
        security (Security): Subclass of Security that is being authorized
        amount (int): How many total shares to authorize -- replaces previous
            amount rather than increment it
        delta (int): Alternative to delta, how many shares to increment or 
            decrement authorized amount by. Either amount or delta may be
            set. If both are set, one can be used to sanity-check the other
            during processing.

    """
    def __init__(self, security, amount=None, delta=None):
        # Validation
        if not isinstance(security, securities.Security):
            raise ValueError("Cls must be an instance of Security")
        if type(amount) != int and type(delta) != int:
            raise ValueError("Must specify integer amount or delta in "
                             "AuthTransaction")

        self.security = security
        self.amount = amount
        self.delta = delta

    def __call__(self, datetime_, state):
        "Processing an AuthTransaction means setting the amount to a set value"
        security_state = state[self.security]
        if self.amount:
            security_state.authorized = self.amount
        elif self.delta:
            security_state.authorized += self.delta
        return state

