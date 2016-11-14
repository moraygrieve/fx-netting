import random, math, copy

from orders import FXOrder, CrossFXOrder, Side
from accounts import Accounts
from prices import getPrice, printPrices, convertTo, convertToMid
from convention import marketConvention

#random.seed(4)  EUR cancel out completely
#random.seed(24)

#random.seed(124)
random.seed(120)


#ACCOUNTS = [('Account A','USD'),('Account B','USD'),('Account C','USD'),('Account D','USD')]
#CURRENCIES = ['AUD','CAD','CHF','CNH', 'EUR','GBP','HKD','JPY','NZD','PLN','USD']

ACCOUNTS = [('Account A','USD'),('Account B','EUR'),('Account C','USD'),('Account D','USD'),('Account E','EUR')]
CURRENCIES = ['AUD','CAD','CHF','GBP','EUR','HKD','JPY','NZD','PLN','USD']


def initAccounts():
    accounts = Accounts(CURRENCIES)
    for accountName, accountCcy in ACCOUNTS: accounts.addAccount(accountName, accountCcy)

    for ccy in CURRENCIES:
        for accountName, accountCcy in ACCOUNTS:
            if ccy == accountCcy: continue
            r = random.randint(-5,5)
            if (r > 2): target_amount = roundup(convertToMid(ccy, accountCcy, 1000000*random.randint(1,10)))
            elif (r < -2): target_amount = roundup(convertToMid(ccy, accountCcy, -1000000*random.randint(1,10)))
            else: continue
            if target_amount == 0: continue

            account_base_amount = convertTo(accountCcy, ccy, target_amount)
            accounts.addAccountTarget(accountName, ccy, target_amount, account_base_amount)
    return accounts

def roundup(amount):
    return int(math.ceil(amount/1000000.0)) * 1000000

def sortedKeys(dict):
    keys = dict.keys()
    keys.sort()
    return keys


def doSplits(accounts):
    splitOrders = {}
    for name in accounts.getAccountNames():
        account = accounts.getAccount(name)
        splitOrders[account.getBase()] = []

        for pair in sortedKeys(account.getOrders()):
            order =  account.getOrders()[pair]
            if account.getBase() == 'USD':
                splitOrders[account.getBase()].append(order)
            if account.getBase() == 'EUR' and pair != 'EURUSD':
                cross = CrossFXOrder(order)
                cross.split('USD')
                splitOrders[account.getBase()].append(cross.left)
                splitOrders[account.getBase()].append(cross.right)


def getTotals(accounts, split=False):
    aggregatedOrders = {}
    nettedOrders = {}
    splitOrders = {}

    #aggregate orders within account of the same base (add buy and sell side)
    for ccy in accounts.currencies:
        for name in accounts.getAccountNames():
            account = accounts.getAccount(name)

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
    for base in sortedKeys(aggregatedOrders):
        nettedOrders[base] = {}

        for pair in sortedKeys(aggregatedOrders[base]):
            buyOrder = aggregatedOrders[base][pair][0]
            sellOrder = aggregatedOrders[base][pair][1]

            if (buyOrder.baseAmount >= sellOrder.baseAmount):
                order = copy.deepcopy(buyOrder)
                order.account = "Netted"
                order.net(order.base if base == order.term else order.term, sellOrder)
            else:
                order = copy.deepcopy(sellOrder)
                order.account = "Netted"
                order.net(order.base if base == order.term else order.term, buyOrder)

            nettedOrders[base][pair] = order

    #split the EUR orders
    if split and nettedOrders.has_key('EUR'):
        for pair in sortedKeys(nettedOrders['EUR']):
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
                            splitOrders[order.pair].setSaving(order.getSaving())
                        else:
                            order.net('EUR', splitOrders[order.pair])
                            order.setSaving(splitOrders[order.pair].getSaving())
                            splitOrders[order.pair] = order
                else:
                    splitOrders[order.pair] = order

        nettedOrders['EUR'] = {}
        for pair in sortedKeys(splitOrders):
            order = splitOrders[pair]
            order.account = "Split EUR"
            nettedOrders['EUR'][pair] = order

    #net across accounts (assume EUR and USD for now)
    for pair in sortedKeys(nettedOrders['USD']):
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
                    buyOrder.setSaving(sellOrder.getSaving())
                    sellOrder.setInternal()
                else:
                    dealtCcy = buyOrder.term if buyOrder.base == sellOrder._base else buyOrder.base
                    sellOrder.net(dealtCcy, buyOrder)
                    sellOrder.setSaving(buyOrder.getSaving())
                    buyOrder.setInternal()
            else:
                order1.aggregate(order2)
                order2.setInternal()

    return nettedOrders

if __name__ == "__main__":
    total = 0
    count = 0
    totals = []

    accounts = initAccounts()
    printPrices()
    accounts.printAccountTargets()
    accounts.printAccountOrders()
    netOrders = getTotals(accounts, True)

    print "\n Netted FX Orders:\n"
    totalSaved = 0
    for base in netOrders:
        for key in sortedKeys(netOrders[base]):
            order = netOrders[base][key]
            if (not order.internal):
                print "%s (saving %8.2f USD)" % (order.__str__(), order.getSaving())
                totalSaved += order.getSaving()

    print "\nTotal USD amount saved across the accounts (using individual trades) %.2f" % totalSaved
    #print "\nTotal USD amount saved across the accounts (using net account flow) %.2f" % (nettedCCYTotal2 - accountCCYTotal1)


