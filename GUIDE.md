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
