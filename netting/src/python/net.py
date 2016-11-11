import random, math

from orders import FXOrder, Side
from accounts import Accounts
from prices import getPrice, printPrices
from convention import marketConvention

random.seed(24)

ACCOUNTS = [('Account A','USD'),('Account B','USD'),('Account C','USD'),('Account D','USD')]
CURRENCIES = ['AUD','CAD','CHF','CNH', 'EUR','GBP','HKD','JPY','NZD','PLN','USD']

#ACCOUNTS = [('Account A','USD'),('Account B','EUR'),('Account C','USD'),('Account D','USD'),('Account E','EUR')]
#CURRENCIES = ['AUD','CAD','CHF','EUR','GBP','HKD','JPY','NZD','PLN','USD']


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

def convertToMid(ccy1, ccy2, amount):
    #Convert to ccy1 from ccy2 amount using the mid price
    pair, base, term = marketConvention(ccy1, ccy2)
    bid, ask = getPrice(pair)
    if ccy1 == term:
        return amount * ((bid + ask)/2)
    elif ccy1 == base:
        return amount / ((bid + ask)/2)

def convertTo(ccy1, ccy2, amount):
    #convert to ccy1 from ccy2 amount, using the bid or ask
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
                    buy = FXOrder.newBuyOrder("Aggregated", base, term, ccy)
                    sell = FXOrder.newSellOrder("Aggregated", base, term, ccy)
                    aggregatedOrders[pair] = (buy, sell)
                order = account.getOrders()[pair]
                if order.isBuy():aggregatedOrders[pair][0].include(order)
                else: aggregatedOrders[pair][1].include(order)

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
            order.side = Side.BUY
            order.price = ask
            order.dealtAmount = aggregatedOrders[pair][0].dealtAmount - aggregatedOrders[pair][1].dealtAmount

            dealtSaved = aggregatedOrders[pair][1].dealtAmount
            if order.dealtCurrency == order.base:
                order.baseAmount = order.dealtAmount
                order.termAmount = order.dealtAmount * order.price
                order.addSaving(dealtSaved*ask - dealtSaved*bid)
            else:
                order.baseAmount = order.dealtAmount / order.price
                order.termAmount = order.dealtAmount
                order.addSaving(dealtSaved/bid - dealtSaved/ask)

        else:
            order.side = Side.SELL
            order.price = bid
            order.dealtAmount = aggregatedOrders[pair][1].dealtAmount - aggregatedOrders[pair][0].dealtAmount

            dealtSaved = aggregatedOrders[pair][0].dealtAmount
            if order.dealtCurrency == order.base:
                order.baseAmount = order.dealtAmount
                order.termAmount = order.dealtAmount * order.price
                order.addSaving(dealtSaved*ask - dealtSaved*bid)
            else:
                order.baseAmount = order.dealtAmount / order.price
                order.termAmount = order.dealtAmount
                order.addSaving(dealtSaved/bid - dealtSaved/ask)

        nettedOrders.append(order)

    return nettedOrders

if __name__ == "__main__":
    total = 0
    count = 0
    totals = []
    for i in range(0,1):
        accounts = initAccounts()
        printPrices()
        accounts.printAccountTargets()
        accounts.printAccountOrders()
        netOrders = getTotals(accounts)

        print ""
        totalSaved = 0
        for order in netOrders:
            saved = order.getSaving()
            contraCurrency = order.base if order.dealtCurrency == order.term else order.term
            if (contraCurrency != 'USD'):
                savedUSD = convertToMid('USD', contraCurrency, saved)
                print "%s - saving %8.2f %s (%8.2f USD)" % (order.__str__(), saved, contraCurrency, savedUSD)
                saved = savedUSD
            else:
                print "%s - saving %8.2f %s" % (order.__str__(), saved, contraCurrency)
            totalSaved += saved

        print "\nTotal USD amount saved across the accounts %.2f" % totalSaved

        total += totalSaved
        count += 1
        totals.append(saved)
    print "Average = %f" % (total /count)

    #totals.sort()
    #hist, bin_edges = numpy.histogram(totals, 100)
    #for i in range(0, len(hist)):
    #    print int(bin_edges[i]), hist[i]
    #print totals

