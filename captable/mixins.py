from __future__ import absolute_import


class EqualityMixin(object):
    """Mixin for simple object equality testing -- ensures equality matches
    if all attributes match
    """
    def __eq__(self, other):
        if other:
            return vars(self) == vars(other)
        return False


class Snowflake(object):
    """Mixin for marking an instance of a class as unique. A copy or deepcopy 
    of a Snowflake using the `copy` module will return a reference to this 
    object rather than a new copy. This is useful when using a class instance
    as an immutable identifier in a dict or object, and you want to create a
    copy of that dict or object while using the same instance as an identifier
    (e.g. for equality checking)
    """
    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self