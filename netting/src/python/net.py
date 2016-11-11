import random, math

from orders import FXOrder
from accounts import Accounts
from prices import getPrice, printPrices
from convention import marketConvention

random.seed(24)

ACCOUNTS = [('Account A','USD'),('Account B','USD'),('Account C','USD'),('Account D','USD')]
CURRENCIES = ['AUD','CAD','CHF','CNH','EUR','GBP','HKD','JPY','NZD','PLN']

def initAccounts():
    accounts = Accounts(CURRENCIES)
    for accountName, accountCcy in ACCOUNTS: accounts.addAccount(accountName, accountCcy)

    for ccy in CURRENCIES:
        for accountName, accountCcy in ACCOUNTS:
            r = random.randint(-5,5)
            if (r > 2): ccy_amount = convertFromMid(ccy, accountCcy, 1000000*random.randint(1,10))
            elif (r < -2): ccy_amount = convertFromMid(ccy, accountCcy, -1000000*random.randint(1,10))
            else: continue
            if ccy_amount == 0: continue

            contra_amount = convertFromSide(ccy, accountCcy, ccy_amount)
            accounts.addAccountTarget(accountName, ccy, ccy_amount, contra_amount)
    return accounts

def roundup(amount):
    return int(math.ceil(amount/1000000.0)) * 1000000

def convertFromMid(ccy1, ccy2, amount):
    pair, base, term = marketConvention(ccy1, ccy2)
    bid, ask = getPrice(pair)
    if ccy1 == term:
        return roundup(amount * ((bid + ask)/2))
    elif ccy1 == base:
        return roundup(amount / ((bid + ask)/2))

def convertFromSide(ccy1, ccy2, amount):
    pair, base, term = marketConvention(ccy1, ccy2)
    bid, ask = getPrice(pair)
    if ccy1 == term:
        if (amount > 0): return -1 * amount / bid
        else: return -1 * amount / ask
    elif ccy1 == base:
        if (amount > 0): return -1 * amount * ask
        else: return -1 * amount * bid

def sortedKeys(dict):
    keys = dict.keys()
    keys.sort()
    return keys

def getTotals(accounts):
    aggregatedOrders = {}
    nettedOrders = []
    for ccy in accounts.currencies :
        for name in accounts.getAccountNames():
            account = accounts.getAccount(name)
            pair, base, term = marketConvention(ccy, account.getBase())

            if account.getOrders().has_key(pair):
                if not aggregatedOrders.has_key(pair):
                    buy = FXOrder()
                    buy.account = "Aggregated"
                    buy.base = base
                    buy.term = term
                    buy.side = "BUY "
                    buy.dealtCurrency = ccy

                    sell = FXOrder()
                    sell.account = "Aggregated"
                    sell.base = base
                    sell.term = term
                    sell.side = "SELL"
                    sell.dealtCurrency = ccy
                    aggregatedOrders[pair] = (buy, sell)

                order = account.getOrders()[pair]
                if order.isBuy():aggregatedOrders[pair][0].include(order)
                else: aggregatedOrders[pair][1].include(order)

    totalSaved = 0
    print ""
    for pair in sortedKeys(aggregatedOrders):
        bid, ask = getPrice(pair)

        order = FXOrder()
        order.account = "Netted"
        order.base = aggregatedOrders[pair][0].base
        order.term = aggregatedOrders[pair][0].term
        order.dealtCurrency = aggregatedOrders[pair][0].dealtCurrency

        buyAmount = aggregatedOrders[pair][0].dealtAmount
        sellAmount = aggregatedOrders[pair][1].dealtAmount
        if (buyAmount >= sellAmount):
            order.side = "BUY "
            order.price = ask
            order.dealtAmount = aggregatedOrders[pair][0].dealtAmount - aggregatedOrders[pair][1].dealtAmount

            dealtSaved = aggregatedOrders[pair][1].dealtAmount
            if order.dealtCurrency == order.base:
                order.baseAmount = order.dealtAmount
                order.termAmount = order.dealtAmount * order.price
                saving = dealtSaved*ask - dealtSaved*bid
            else:
                order.baseAmount = order.dealtAmount / order.price
                order.termAmount = order.dealtAmount
                saving = dealtSaved/bid - dealtSaved/ask

        else:
            order.side = "SELL"
            order.price = bid
            order.dealtAmount = aggregatedOrders[pair][1].dealtAmount - aggregatedOrders[pair][0].dealtAmount

            dealtSaved = aggregatedOrders[pair][0].dealtAmount
            if order.dealtCurrency == order.base:
                order.baseAmount = order.dealtAmount
                order.termAmount = order.dealtAmount * order.price
                saving = dealtSaved*ask - dealtSaved*bid
            else:
                order.baseAmount = order.dealtAmount / order.price
                order.termAmount = order.dealtAmount
                saving = dealtSaved/bid - dealtSaved/ask

        totalSaved += saving
        if (order.baseAmount > 0):
            nettedOrders.append(order)
            print "%s - saving %.2f USD" % (order.__str__(), saving)
    print "\nTotal USD amount saved across the accounts %.2f" % totalSaved
    return totalSaved, nettedOrders

if __name__ == "__main__":
    total = 0
    count = 0
    totals = []
    for i in range(0,1):
        accounts = initAccounts()
        printPrices()
        accounts.printAccountTargets()
        accounts.printAccountOrders()
        saved, netOrders = getTotals(accounts)

        total += saved
        count += 1
        totals.append(saved)
    print "Average = %f" % (total /count)

    #totals.sort()
    #hist, bin_edges = numpy.histogram(totals, 100)
    #for i in range(0, len(hist)):
    #    print int(bin_edges[i]), hist[i]
    #print totals

