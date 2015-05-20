"""For tracking the different types and classes of securities in a table
"""
from __future__ import absolute_import

from . import mixins
from .misc import classproperty


class Security(mixins.Snowflake):
    """Represents a class or type of Security

    Args:
        holder (Person) - The legal Person holding this Security
        cert_no (str) - Optional user-assigned sring identifier for this
            Security, defaults to None

    Properties:
        holder (Person) - The legal Person holding this Security
        issued_on (datetime) - When this Security was issued
        cert_no (str) - User-assigned sring identifier for this Security, if
            provided
        cert_name (str) - The actual name on the security. Defaults to the name
            property of the holder, but may be set to anything (e.g. for when
            the certificate is addressed to one party but held by another, or
            if a Person changes its name)
        cancelled (bool) - If true, then this security has been cancelled.
            Defaults to False.

    """
    # This variable is used to determine the key in a CapTable's state dict 
    # under which we store security info
    STATE_KEY = 'securities'

    @classproperty
    def name(cls):
        """The name of this class of stock -- used to link together
        different (successor) classes for what's intended to be the same
        class of security"""
        raise NotImplementedError
            
    @classmethod
    def __table_key__(cls, state):
        """A Security *class* can be used as a key in the CapTable state.

        Returns a SecuritiesState object, if applicable. Else raises a 
        KeyError.
        """
        ret = state.get(cls.STATE_KEY, {}).get(cls.name, None)
        if ret != None:
            return ret
        raise KeyError("No state for that security")

    @classmethod
    def _in(cls, state):
        "Less ugly alias to __table_key__"
        return cls.__table_key__(state)

    @classmethod
    def auth(cls):
        """Returns a callable that functions as a transaction for CapTable.
        Transaction will construct an instance of the MetaState for this
        Security class unless it already exists.

        If MetaState already exists but does not match the MetaState of this
        Security's class, the MetaState will be updated to the new class
        while preserving the __dict__ of the old class.
        """
        def txn(datetime_, state):
            securities_dict = state.setdefault(cls.STATE_KEY, {})
            current_state = securities_dict.get(cls.name, None)
            if not current_state:
                securities_dict[cls.name] = cls.MetaState()
            elif not isinstance(current_state, cls.MetaState):
                securities_dict[cls.name] = \
                    cls.MetaState.__migrate__(current_state)
            return state
        return txn

    class MetaState(mixins.EqualityMixin):
        """A class containing information about an entire *class* of securities
        as opposed to just one instance (issuance). Used by auth. Can be sub-
        classed or overriden as appropriate, but should have a __migrate__ 
        classmethod.

        """
        @classmethod
        def __migrate__(cls, old_state):
            """Returns an instance of this class instantiated from a
            pre-decessor MetaState"""
            ret = cls()
            ret.__dict__ = old_state.__dict__
            return ret

        def __init__(self):
            # Used to store issuances in order
            self.issuances = []

            # Used to reference issuances by certifiate number (if applicable)
            self.cert_no_lookups = {}

        def issue(self, issuance):
            self.issuances.append(issuance)
            if issuance.cert_no:
                if issuance.cert_no in self.cert_no_lookups:
                    raise ValueError("cert_no %s already in use" % 
                                     issuance.cert_no)
                else:
                    self.cert_no_lookups[issuance.cert_no] = issuance

        def __getitem__(self, key):
            return self.cert_no_lookups[key]

        def __contains__(self, key):
            return key in self.cert_no_lookups

    @classmethod
    def issue(cls, *args, **kwds):
        """Returns a callable issuing stock to a holder"""
        def txn(datetime_, state):
            try:
                metastate = cls._in(state)
            except KeyError:
                raise RuntimeError("Need to authorize security before issuing")

            security = cls(*args, **kwds)
            security.issued_on = datetime_
            metastate.issue(security)
            return state
        return txn

    @classmethod
    def transfer(cls, cert_no, to):
        """Returns a transaction transfering a certificate from one holder to 
        another. A transfer does not change the name or values on the
        certificate. It only changes the holder. 
        """
        def txn(datetime_, state):
            metastate = cls._in(state)
            issuance = metastate[cert_no]
            issuance.holder = to
            return state
        return txn

    @classmethod
    def cancel(cls, cert_no):
        """Cancels a particular certificate number"""
        def txn(datetime_, state):
            metastate = cls._in(state)
            issuance = metastate[cert_no]
            issuance.cancelled = True
            return state
        return txn

    def __init__(self, holder, cert_no=None, cert_name=None):
        self.holder = holder
        self.cert_no = cert_no
        self.cert_name = cert_name or holder.name
        self.cancelled = False

        # Assign datetime when called via transaction
        self.issued_on = None


class Stock(Security):
    """Represents non-fractional shares of stock in a Company

    Args:
        holder (Person) - The legal Person holding this Security
        amount (int) - The integer amount of shares
        cert_no (str) - Optional user-assigned sring identifier for this 
            Security, defaults to None

    Properties:
        holder (Person) - The legal Person holding this Security
        issued_on (datetime) - When this Security was issued
        amount (int) - The integer amount of shares
        cert_no (str) - User-assigned sring identifier for this Security, if
            provided
    """
    @classmethod
    def auth(cls, amount=None, delta=None):
        """Return tranaction authorizing a certain number of shares of stock for
        issuance"""
        def txn(datetime_, state):
            state = super(Stock, cls).auth()(datetime_, state)
            metastate = cls._in(state)

            # If both supplied, validate (amount var will alter state in below)
            if type(amount) == int and type(delta) == int:
                assert metastate.authorized + delta == amount, \
                "Authorization amount inconsistent delta: %s + %s != %s" % \
                (metastate.authorized, delta, amount)

            # If amount, replace
            if type(amount) == int:
                metastate.authorized = amount

            # If only delta, increment
            elif type(delta) == int:
                metastate.authorized += delta

            return state
        return txn

    class MetaState(Security.MetaState):
        """Track authorized number of shares in addition to other security info
        """
        def __init__(self):
            super(Stock.MetaState, self).__init__()
            self.authorized = 0

        @property
        def outstanding(self):
            """Number of shares issued and outstanding"""
            return self.issued # TODO - update for retired shares

        @property
        def issued(self):
            """Number of shares issued, which may or may not be outstanding"""
            return sum(map(
                    (lambda i: 0 if i.cancelled else i.amount), 
                    self.issuances))

        @property
        def reserved(self):
            """Number of shares reserved for later issuance"""
            return 0 #TODO
            
        @property
        def issuable(self):
            """Number of shares available for issuance"""
            return self.authorized - self.outstanding
        
        @property
        def unreserved(self):
            """Number of shares avilable for issuance after taking into account
            reserved shares"""
            return self.issuable - self.reserved

        def issue(self, issuance):
            assert self.issued + issuance.amount < self.authorized, \
                "Insufficient authorized: %s < %s + %s" % (
                self.authorized, issuance.amount, self.issued)
            return super(Stock.MetaState, self).issue(issuance)

    def __init__(self, holder, amount, cert_no=None):
        super(Stock, self).__init__(holder=holder, cert_no=cert_no)
        self.amount = amount
    

class CommonStock(Stock):
    name = "Common Stock"

