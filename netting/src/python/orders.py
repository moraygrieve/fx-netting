class Side:
    BUY = "BUY"
    SELL = "SELL"

class FXOrder:

    @staticmethod
    def newBuyOrder(account, base, term, dealtCurrency):
        order = FXOrder()
        order.account = account
        order.base = base
        order.term = term
        order.side = Side.BUY
        order.dealtCurrency = dealtCurrency
        return order

    @staticmethod
    def newSellOrder(account, base, term, dealtCurrency):
        order = FXOrder()
        order.account = account
        order.base = base
        order.term = term
        order.side = Side.SELL
        order.dealtCurrency = dealtCurrency
        order.saving = 0
        return order

    def __init__(self):
        self.account = ""
        self.base = ""
        self.term = ""
        self.side = None
        self.price = 0.0
        self.baseAmount = 0
        self.termAmount = 0
        self.dealtCurrency = ""
        self.dealtAmount = 0

    def isBuy(self):
        return self.side == Side.BUY

    def addSaving(self, saving):
        self.saving = saving

    def getSaving(self):
        return self.saving

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
        fstring = "[%-10s] %-4s  %s%s  %12.2f @ %-10.5f %10d %s dealt "
        if self.dealtCurrency == 'JPY': fstring = "[%-10s] %-4s  %s%s  %12.2f @ %-10.2f %10d %s dealt "
        return fstring % \
               (self.account, self.side, self.base, self.term, self.baseAmount, self.price, self.dealtAmount, self.dealtCurrency)
