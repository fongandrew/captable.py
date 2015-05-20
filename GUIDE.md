Captable.py Guide
=================

Transactions
------------

Captable.py models a cap table as a a series of transactions. Each transaction
is simply a callable (or list of callables) that receives a datetime and the 
current state of the table (a dict), and returns modified state.

To record a transaction, use the `record` method. Transactions are processed
immediately after recording.

```python
table = captable.CapTable()

def txn1(datetime_, state):
    state["key_1"] = 1
    return state

def txn2(datetime_, state):
    state["key_2"] = 2
    return state

table.record(datetime.datetime.now(), txn1, txn2)
```

Transactions are atomic. If any of the callables in the transaction raises an
exception, the entire transaction fails and the state of the table remains at
what it was prior to recording the transaction.

Securities
----------

Captables primarily exist to track a company's securities. Each security
issuance should be represented by an instance of the Security class. A separate
Security instance should be used to keep track of each security certificate.
Although a company may not issue actual certificates, much of captable.py 
implicitly assumes that the company is keeping track of its security
issuances via virtual "certificates" held by various persons, as opposed to a
simple mapping of numbers of shares or dollars to holders.

### Stock Concepts

Stock is modelled as a subclass of Security. It is built around the following
concepts.

*Authorized Shares* - All shares of stock must first be authorized for issuance.
The number of issued shares may never exceed the number authorized.

*Issued Shares* - Shares of stock are issued when a company allocates the
shares for distribution. In practice, this means that a Stock Certificate of
some kind has been created to represent the shares.

*Outstanding Shares* - Outstanding shares are issued shares that are held by a
third party. Captable.py interprets any Security instance with a truthy
`holder` attribute as outstanding.

*Treasury Shares* - Treasury shares are issued shares that are held by the
issuer (e.g. they were never issued or were repurchased). Treasury shares are
not oustanding. Captable.py models treasury shares with a Security instance
with a falsely `holder` attribute.

*Cancelled Shares* - Captable.py treats cancellation as the equivalent of 
de-allocating shares. Cancelled shares are no longer issued or outstanding.

*Retired Shares* - Retired shares are treated as cancelled shares. In addition,
if the `DEAUTH_RETIRED` attribute is set to True on the relevant Security class,
retired shares can not be reissued. This has the effect of amending the total 
authorized shares down by the retired amount. By default, DEAUTH_RETIRED is
False.