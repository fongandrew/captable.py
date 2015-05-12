from __future__ import absolute_import

import captable

class StubTransaction(captable.Transaction):
    """
    Helper used for testing purposes
    """
    def process(self, state):
        if not hasattr(state, "stubs_processed"):
            state.stubs_processed = []
        state.stubs_processed.append(self);

    @classmethod
    def check(cls, state, *txns):
        if hasattr(state, 'stubs_processed'):
            assert state.stubs_processed == list(txns)
        else:
            assert (not txns), "Stubs processed not set"
