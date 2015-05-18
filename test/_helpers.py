from __future__ import absolute_import

import captable
from captable.mixins import Snowflake

class StubTransaction(Snowflake):
    """
    Helper used for testing purposes
    """
    def __call__(self, datetime_, state):
        if not hasattr(state, "stubs_processed"):
            state.stubs_processed = []
        state.stubs_processed.append(self);
        return state

    @classmethod
    def check(cls, state, *txns):
        if hasattr(state, 'stubs_processed'):
            assert state.stubs_processed == list(txns)
        else:
            assert (not txns), "Stubs processed not set"

class ErrorTransaction(StubTransaction):
    """Simulates an exception raised after state changes"""
    def __call__(self, state):
        state = super(ErrorTransaction, self).process(state)
        raise RuntimeError("Boom")