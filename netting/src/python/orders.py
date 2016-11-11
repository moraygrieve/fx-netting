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
