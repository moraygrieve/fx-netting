import random, copy

from orders import FXOrder, CrossFXOrder
from accounts import Accounts
from prices import printPrices
from convention import marketConvention

random.seed(120)
ACCOUNTS = [('Account A','USD'),('Account B','EUR'),('Account C','USD'),('Account D','USD'),('Account E','EUR')]
CURRENCIES = ['AUD','CAD','CHF','GBP','EUR','HKD','JPY','NZD','PLN','USD']


class Netter:

    def __init__(self, account, split):
        self.account = account
        self.split = split

    def sortedKeys(self, dict):
        keys = dict.keys()
        keys.sort()
        return keys

    def net(self):
        aggregatedOrders = {}
        nettedOrders = {}
        splitOrders = {}

        #aggregate orders within account of the same base (add buy and sell side)
        for ccy in self.account.currencies:
            for name in self.account.getAccountNames():
                account = self.account.getAccount(name)

                if (not aggregatedOrders.has_key(account.getBase())): aggregatedOrders[account.getBase()] = {}
                pair, base, term = marketConvention(ccy, account.getBase())

                if account.getOrders().has_key(pair):
                    order = account.getOrders()[pair]

                    if not aggregatedOrders[account.getBase()].has_key(pair):
                        buy = FXOrder.newBuyOrder("Aggregated", base, term)
                        sell = FXOrder.newSellOrder("Aggregated", base, term)
                        aggregatedOrders[account.getBase()][pair] = (buy, sell)

                    if order.isBuy():aggregatedOrders[account.getBase()][pair][0].aggregate(order)
                    else: aggregatedOrders[account.getBase()][pair][1].aggregate(order)

        #net aggregates within accounts of the same base (add the buy and sell)
        for accountCcy in self.sortedKeys(aggregatedOrders):
            nettedOrders[accountCcy] = {}

            for pair in self.sortedKeys(aggregatedOrders[accountCcy]):
                buyOrder = aggregatedOrders[accountCcy][pair][0]
                sellOrder = aggregatedOrders[accountCcy][pair][1]

                if (buyOrder.baseAmount >= sellOrder.baseAmount):
                    order = copy.deepcopy(buyOrder)
                    order.account = "Netted"
                    order.net(order.base if accountCcy == order.term else order.term, sellOrder)
                else:
                    order = copy.deepcopy(sellOrder)
                    order.account = "Netted"
                    order.net(order.base if accountCcy == order.term else order.term, buyOrder)

                nettedOrders[accountCcy][pair] = order

        #split the EUR orders
        if self.split and nettedOrders.has_key('EUR'):
            for pair in self.sortedKeys(nettedOrders['EUR']):
                nettedOrder = nettedOrders['EUR'][pair]
                if nettedOrder.pair in  ['EURUSD']:
                    if not splitOrders.has_key(nettedOrder.pair):
                        splitOrders[nettedOrder.pair] = copy.deepcopy(nettedOrder)
                    continue

                cross = CrossFXOrder(nettedOrder)
                cross.split('USD', nettedOrder.base if nettedOrder.base != 'EUR' else nettedOrder.term)

                for order in [cross.left, cross.right]:
                    if splitOrders.has_key(order.pair):

                        if (splitOrders[order.pair].side == order.side):
                            splitOrders[order.pair].aggregate(order)
                        else:
                            if splitOrders[order.pair].baseAmount >= order.baseAmount:
                                splitOrders[order.pair].net('EUR', order)
                            else:
                                order.net('EUR', splitOrders[order.pair])
                                splitOrders[order.pair] = order
                    else:
                        splitOrders[order.pair] = order

            nettedOrders['EUR'] = {}
            for pair in self.sortedKeys(splitOrders):
                order = splitOrders[pair]
                order.account = "Split EUR"
                nettedOrders['EUR'][pair] = order

        #net across accounts (assume EUR and USD for now)
        for pair in self.sortedKeys(nettedOrders['USD']):
            order1 = nettedOrders['USD'][pair]
            order1._base = 'USD'

            if nettedOrders.has_key('EUR') and nettedOrders['EUR'].has_key(pair):
                order2 = nettedOrders['EUR'][pair]
                order2._base = 'EUR'

                if order1.side != order2.side:
                    buyOrder = order1 if order1.isBuy() else order2
                    sellOrder = order2 if order1.isBuy() else order1

                    if (buyOrder.baseAmount >= sellOrder.baseAmount):
                        dealtCcy = sellOrder.term if sellOrder.base == buyOrder._base else sellOrder.base
                        buyOrder.net(dealtCcy, sellOrder)
                    else:
                        dealtCcy = buyOrder.term if buyOrder.base == sellOrder._base else buyOrder.base
                        sellOrder.net(dealtCcy, buyOrder)
                else:
                    order1.aggregate(order2)

        totalSaved = 0
        sortedOrders = {}
        for base in nettedOrders:
            for key in self.sortedKeys(nettedOrders[base]):
                if (not nettedOrders[base][key].internal):
                    sortedOrders[key] = nettedOrders[base][key]
                    totalSaved += sortedOrders[key].getSaving()
        return totalSaved, sortedOrders


if __name__ == "__main__":
    total = 0
    count = 0
    totals = []

    printPrices()
    accounts = Accounts(CURRENCIES)
    accounts.initAccounts(ACCOUNTS)
    accounts.printAccountTargets()
    accounts.printAccountOrders(table=True)
    spreadCost = accounts.getSpreadCost()

    netter = Netter(accounts, True)
    saved, netOrders = netter.net()

    print "\nNetted FX Orders:\n"
    for pair in netter.sortedKeys(netOrders):
        order = netOrders[pair]
        print "%s (saving %8.2f USD)" % (order.__str__(), order.getSaving())

    print "\nTotal USD amount saved across the accounts (using individual trades) %.2f" % saved
    print "This equates to %5.2f percent cost on the spread " % ((saved/spreadCost)*100.0)


