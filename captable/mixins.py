from __future__ import absolute_import

class EqualityMixin(object):
    """Mixin for simple object equality testing -- ensures equality matches
    if all attributes match
    """
    def __eq__(self, other):
        return vars(self) == vars(other)
