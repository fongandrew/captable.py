from __future__ import absolute_import

import captable
from captable.mixins import Snowflake

class StubTransaction(Snowflake):
    """
    Helper used for testing purposes
    """
    def __call__(self, datetime_, state):
        processed = state.setdefault("stubs_processed", [])
        processed.append(self);
        return state

    @classmethod
    def check(cls, state, *txns):
        processed = state.get("stubs_processed", [])
        assert processed == list(txns)

    @classmethod
    def count(cls, state):
        processed = state.get("stubs_processed", [])
        return len(processed)


class ErrorTransaction(StubTransaction):
    """Simulates an exception raised after state changes"""
    def __call__(self, *args, **kwds):
        state = super(ErrorTransaction, self).__call__(*args, **kwds)
        raise RuntimeError("Boom")