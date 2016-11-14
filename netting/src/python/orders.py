import math

from convention import marketConvention
from prices import getPrice, convertToMid

class Side:
    BUY = "BUY"
    SELL = "SELL"


class CrossFXOrder:
    def __init__(self, order):
        self.order = order
        self.left = None
        self.right = None

    def split(self, splitCcy, primaryCcy):
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

        self.left = leftOp(self.order.account, base1, term1)
        self.right = rightOp(self.order.account, base2, term2)
        self.left.account += "-SL"
        self.right.account += "-SR"

        #set the amounts (primaryCcy is the one kept constant)
        if (primaryCcy == self.order.base):
            self.left.setAmounts(self.order.base, self.order.baseAmount)
            self.right.setAmounts(splitCcy, self.left.baseAmount if self.left.base == splitCcy else self.left.termAmount)
        else:
            self.right.setAmounts(self.order.term, self.order.termAmount)
            self.left.setAmounts(splitCcy, self.right.baseAmount if self.right.base == splitCcy else self.right.termAmount)


class FXOrder:

    @staticmethod
    def newBuyOrder(account, base, term):
        """Static method to create and return a new buy order.
        """
        order = FXOrder()
        order.account = account
        order.base = base
        order.term = term
        order.pair = base+term
        order.side = Side.BUY
        return order

    @staticmethod
    def newSellOrder(account, base, term):
        """Static method to create and return a new sell order.
        """
        order = FXOrder()
        order.account = account
        order.base = base
        order.term = term
        order.pair = base+term
        order.side = Side.SELL
        return order


    def __init__(self):
        """Default constructor.
        """
        self.account = None
        self.base = None
        self.term = None
        self.side = None
        self.price = 0.0
        self.baseAmount = 0
        self.termAmount = 0
        self.saving = 0
        self.internal = False


    def setAmounts(self, ccy, amount, priceFavor=False):
        """Set the amounts for this order base on a given currency amount.

        The method will obtain the bid and ask price from the static price service, and then
        calculate the amount of the contra currency based on the price. If the order is a buy
        we use the ask price, else we use the bid price (we are taking from the market). If
        the price is favorable for us, we buy at the bid and sell at the ask (making the market).

        @param ccy: The currency of the supplied amount
        @param amount: The supplied amount for the conversion
        @param priceFavor: True if buy at the bid
        """
        bid, ask = getPrice(self.pair)
        if priceFavor: self.price = bid if self.isBuy() else ask
        else: self.price = ask if self.isBuy() else bid
        if (self.base == ccy):
            self.baseAmount = amount
            self.termAmount = amount * self.price
        else:
            self.baseAmount = amount / self.price
            self.termAmount = amount


    def isBuy(self):
        """Return true if this is a buy order.
        """
        return self.side == Side.BUY


    def setSaving(self, saving):
        """Add a saving to the total saving on this order.
        """
        self.saving += saving


    def getSaving(self):
        """Get the total saving on this order.
        """
        return self.saving


    def setInternal(self):
        """Mark this order as being internal (netted out against another order of the same pair)
        """
        self.internal = True


    def aggregate(self, order):
        """Aggregate two orders for the same pair, side and price.

        This is a simple case of adding the base and term amounts, as the pair and
        price of the order to aggregate is that same as this order.

        @param order: The order to new against
        """
        self.base = order.base
        self.term = order.term
        self.side = order.side
        self.price = order.price
        self.baseAmount += order.baseAmount
        self.termAmount += order.termAmount


    def net(self, dealtCcy, order):
        """Net this order against another other for the same pair, opposite side and price.

        Note this order must have the larger base amount. We modify the dealtCurrency amount
        down and use the price of this order to calculate the new term amount base on the order
        price. To calculate the saving we determine the difference in the contra amount between
        the new netted order, and the original order and order used in the netting. If the
        contra currency is not USD, we convert the saving into a USD equivalent using the mid price.

        @param dealtCcy: The currency dealt (need exact amounts)
        @param order: The order to new against
        """
        contraCcy = self.term if self.base == dealtCcy else self.base

        if dealtCcy == self.base:
            contraAmount = self.termAmount
            self.setAmounts(self.base, self.baseAmount - order.baseAmount)
            saving = contraAmount - (self.termAmount + order.termAmount)
        else:
            contraAmount = self.baseAmount
            self.setAmounts(self.term, self.termAmount - order.termAmount)
            saving = contraAmount - (self.baseAmount + order.baseAmount)
        saving = math.fabs(saving)

        if contraCcy != 'USD': self.setSaving(convertToMid('USD', contraCcy, saving))
        else: self.setSaving(saving)


    def __str__(self):
        """Override the string method to print more useful detail of this order.
        """
        internal = "*" if self.internal else ""
        fstring = "[%-10s]%1s %-4s  %s%s  %12.2f @ %-10.5f (contra %12.2f) "
        if self.base == 'JPY' or self.term == 'JPY': fstring = "[%-10s]%1s %-4s  %s%s  %12.2f @ %-10.2f (contra %12.2f) "
        return fstring % \
               (self.account, internal, self.side, self.base, self.term, self.baseAmount, self.price, self.termAmount)


#entry point for some simple testing
if __name__ == "__main__":
    order = FXOrder.newSellOrder('A1','EUR','GBP')
    order.setAmounts('GBP', 1000000)
    print order

    split = CrossFXOrder(order)
    split.split('USD','GBP')
    print split.left
    print split.right
