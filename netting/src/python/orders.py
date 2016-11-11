from convention import marketConvention

class Side:
    BUY = "BUY"
    SELL = "SELL"


class CrossFXOrder:
    def __init__(self, order):
        self.order = order

    def split(self, splitCcy):
        pair1, base1, term1 = marketConvention(self.order.base, splitCcy)
        pair2, base2, term2 = marketConvention(self.order.term, splitCcy)

        if self.order.isBuy():
            if self.order.base == base1: leftOp = FXOrder.newBuyOrder
            else: leftOp  = FXOrder.newSellOrder

            if self.order.term == term2: rightOp = FXOrder.newBuyOrder
            else: rightOp = FXOrder.newSellOrder

        else:
            if self.order.base == base1: leftOp = FXOrder.newSellOrder
            else: leftOp  = FXOrder.newBuyOrder

            if self.order.term == term2: rightOp = FXOrder.newSellOrder
            else: rightOp = FXOrder.newBuyOrder


        left  = leftOp(self.order.account, base1, term1, self.order.dealtCurrency if self.order.dealtCurrency in pair1 else splitCcy)
        right  = rightOp(self.order.account, base2, term2, self.order.dealtCurrency if self.order.dealtCurrency in pair2 else splitCcy)

        print left
        print right

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


if __name__ == "__main__":
    order = FXOrder.newBuyOrder('A1','EUR','JPY','JPY')
    print order

    split = CrossFXOrder(order)
    split.split('USD')