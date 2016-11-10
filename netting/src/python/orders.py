import math
from prices import getPrice
from convention import marketConvention

class FXOrder:
    def __init__(self):
        self.account = ""
        self.base = ""
        self.term = ""
        self.side = ""
        self.price = 0.0
        self.baseAmount = 0
        self.termAmount = 0
        self.dealtCurrency = ""
        self.dealtAmount = 0

    def isBuy(self):
        return self.side == "BUY "

    def include(self, order):
        self.base = order.base
        self.term = order.term
        self.side = order.side
        self.price = order.price
        self.baseAmount += order.baseAmount
        self.termAmount += order.termAmount
        self.dealtCurrency = order.dealtCurrency
        self.dealtAmount += order.dealtAmount

    def __str__(self):
        fstring = "[%-10s] %s  %s%s  %12.2f @ %-10.5f (%-10d dealt %s)"
        if self.dealtCurrency == 'JPY': fstring = "[%-10s] %s  %s%s  %12.2f @ %-10.2f (%-10d dealt %s)"
        return fstring % \
               (self.account, self.side, self.base, self.term, self.baseAmount, self.price, self.dealtAmount, self.dealtCurrency)

class AccountOrders:
    def __init__(self):
        self.orders = {}

    def addToAccount(self, account, denomination, ccy, ccy_amount, contra_amount):
        ccypair, base, term = marketConvention(ccy, denomination)
        bid, ask = getPrice(ccypair)
        order = FXOrder()
        order.account = account
        order.base = base
        order.term = term
        order.dealtCurrency = ccy
        order.dealtAmount = math.fabs(ccy_amount)
        if ccy == base:
            if ccy_amount > 0:
                order.price = ask
                order.side = "BUY "
            else:
                order.price = bid
                order.side = "SELL"
            order.baseAmount = math.fabs(ccy_amount)
            order.termAmount = math.fabs(contra_amount)
        else:
            if ccy_amount > 0:
                order.price = bid
                order.side = "SELL"
            else:
                order.price = ask
                order.side = "BUY "
            order.baseAmount = math.fabs(contra_amount)
            order.termAmount = math.fabs(ccy_amount)
        if not self.orders.has_key(account): self.orders[account]={}
        self.orders[account][order.base+order.term]=order
        return order
