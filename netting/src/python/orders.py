from convention import marketConvention
from prices import getPrice

class Side:
    BUY = "BUY"
    SELL = "SELL"


class CrossFXOrder:
    def __init__(self, order):
        self.order = order
        self.left = None
        self.right = None

    def split(self, splitCcy):
        pair1, base1, term1 = marketConvention(self.order.base, splitCcy)
        pair2, base2, term2 = marketConvention(self.order.term, splitCcy)

        #create the initial orders
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

        self.left = leftOp(self.order.account, base1, term1, self.order.dealtCurrency if self.order.dealtCurrency in pair1 else splitCcy)
        self.right = rightOp(self.order.account, base2, term2, self.order.dealtCurrency if self.order.dealtCurrency in pair2 else splitCcy)

        #set the amounts
        if (self.left.dealtCurrency == order.dealtCurrency):
            self.left.setAmounts(order.dealtAmount)
            self.right.setAmounts(self.left.contraAmount())
        else:
            self.right.setAmounts(order.dealtAmount)
            self.left.setAmounts(self.right.contraAmount())


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
        return order

    def __init__(self):
        self.account = None
        self.base = None
        self.term = None
        self.side = None
        self.dealtCurrency = None
        self.price = 0.0
        self.baseAmount = 0
        self.termAmount = 0
        self.dealtAmount = 0
        self.saving = 0
        self.internal = False

    def setAmounts(self, dealtAmount, priceFavor=False):
        bid, ask = getPrice(self.base+self.term)
        if priceFavor: self.price = bid if self.isBuy() else ask
        else: self.price = ask if self.isBuy() else bid
        self.dealtAmount = dealtAmount
        if (self.base == self.dealtCurrency):
            self.baseAmount = dealtAmount
            self.termAmount = dealtAmount * self.price
        else:
            self.baseAmount = dealtAmount / self.price
            self.termAmount = dealtAmount

    def isBuy(self):
        return self.side == Side.BUY

    def setSaving(self, saving):
        self.saving += saving

    def getSaving(self):
        return self.saving

    def setInternal(self):
        self.internal = True

    def contraCurrency(self):
        return self.base if self.dealtCurrency == self.term else self.term

    def contraAmount(self):
        amount = self.baseAmount if self.dealtCurrency == self.term else self.termAmount
        if self.isBuy() and self.base == self.dealtCurrency: return -1.0 * amount
        if not self.isBuy() and self.term == self.dealtCurrency: return -1.0 * amount
        return amount

    def aggregate(self, order):
        #aggregating orders of same pair, same dealt, same side
        self.base = order.base
        self.term = order.term
        self.side = order.side
        self.price = order.price
        self.baseAmount += order.baseAmount
        self.termAmount += order.termAmount
        self.dealtAmount += order.dealtAmount

    def net(self, order):
        #netting an order of same pair, against one of the opposite side
        self.baseAmount -= order.baseAmount
        self.termAmount = self.baseAmount * self.price

        dealtSaved = order.baseAmount if order.base == self.dealtCurrency else order.termAmount
        self.dealtAmount -= dealtSaved

        bid, ask = getPrice(self.base+self.term)
        if self.dealtCurrency == self.base:
            self.setSaving(dealtSaved*ask - dealtSaved*bid)
        else:
            self.setSaving(dealtSaved/bid - dealtSaved/ask)

    def __str__(self):
        if self.internal: pass
        internal = "*" if self.internal else ""
        fstring = "[%-10s]%1s %-4s  %s%s  %12.2f @ %-10.5f %10d %s dealt "
        if self.dealtCurrency == 'JPY': fstring = "[%-10s]%1s %-4s  %s%s  %12.2f @ %-10.2f %10d %s dealt "
        return fstring % \
               (self.account, internal, self.side, self.base, self.term, self.baseAmount, self.price, self.dealtAmount, self.dealtCurrency)


if __name__ == "__main__":
    order = FXOrder.newSellOrder('A1','EUR','GBP','GBP')
    order.setAmounts(1000000)
    print order

    split = CrossFXOrder(order)
    split.split('USD')
    print split.left
    print split.right
