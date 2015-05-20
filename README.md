captable.py
===========

Tests
-----
Tests are run using [py.test](https://pytest.org/). Enter the following (from
the root of this repository) to set up requirements:

```
pip install -e captable
pip install pytest
```

Then enter `py.test` to run tests.

TODO
----
* [x] Transaction processing basics
* [x] Transactional failure, rollback
* [x] Authorization of Stock
* [x] Validation rules
* [x] Persons
* [x] Issuance of Stock
* [ ] Retirement of Stock
* [ ] Convertible Securities
  * [ ] Prefered Stock
  * [ ] Convertible Debt
* [ ] Stock Plans
  * [ ] Options
* [ ] Reservation of Stock
* [ ] Vesting
* [ ] External events / timing (e.g. vest based on sales)
* [ ] Expiration of Securities
* [ ] Waterfall/Liquidation Analysis
* [ ] Related Persons / Voting Analysis