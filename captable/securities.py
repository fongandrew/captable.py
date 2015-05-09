"""For tracking the different types and classes of securities in a table
"""
class Security(object):
    pass

class Stock(Security):
    pass

class CommonStock(Stock):
    name = "Common Stock"