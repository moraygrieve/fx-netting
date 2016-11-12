import random, math

from orders import FXOrder, Side
from accounts import Accounts
from prices import getPrice, printPrices, convertTo, convertToMid
from convention import marketConvention

#random.seed(4)  EUR cancel out completely
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

def getTotals(accounts):
    aggregatedOrders = {}
    nettedOrders = {}

    #aggregate orders within account of the same base (add buy and sell side)
    for ccy in accounts.currencies:
        for name in accounts.getAccountNames():
            account = accounts.getAccount(name)

            if (not aggregatedOrders.has_key(account.getBase())): aggregatedOrders[account.getBase()] = {}
            pair, base, term = marketConvention(ccy, account.getBase())

            if account.getOrders().has_key(pair):
                if not aggregatedOrders[account.getBase()].has_key(pair):
                    buy = FXOrder.newBuyOrder("Aggregated", base, term, ccy)
                    sell = FXOrder.newSellOrder("Aggregated", base, term, ccy)
                    aggregatedOrders[account.getBase()][pair] = (buy, sell)
                order = account.getOrders()[pair]
                if order.isBuy():aggregatedOrders[account.getBase()][pair][0].include(order)
                else: aggregatedOrders[account.getBase()][pair][1].include(order)

    #net aggregates within accounts of the same base (add the buy and sell)
    for base in sortedKeys(aggregatedOrders):
        nettedOrders[base] = {}

        for pair in sortedKeys(aggregatedOrders[base]):
            bid, ask = getPrice(pair)

            order = FXOrder()
            order.account = "Netted"
            order.base = aggregatedOrders[base][pair][0].base
            order.term = aggregatedOrders[base][pair][0].term
            order.dealtCurrency = aggregatedOrders[base][pair][0].dealtCurrency

            buyAmount = aggregatedOrders[base][pair][0].dealtAmount
            sellAmount = aggregatedOrders[base][pair][1].dealtAmount

            if (buyAmount >= sellAmount):
                order.side = Side.BUY
                order.setAmounts(aggregatedOrders[base][pair][0].dealtAmount - aggregatedOrders[base][pair][1].dealtAmount)
                dealtSaved = aggregatedOrders[base][pair][1].dealtAmount
                if order.dealtCurrency == order.base:
                    order.addSaving(dealtSaved*ask - dealtSaved*bid)
                else:
                    order.addSaving(dealtSaved/bid - dealtSaved/ask)

            else:
                order.side = Side.SELL
                order.setAmounts(aggregatedOrders[base][pair][1].dealtAmount - aggregatedOrders[base][pair][0].dealtAmount)
                dealtSaved = aggregatedOrders[base][pair][0].dealtAmount
                if order.dealtCurrency == order.base:
                    order.addSaving(dealtSaved*ask - dealtSaved*bid)
                else:
                    order.addSaving(dealtSaved/bid - dealtSaved/ask)

            nettedOrders[base][pair] = order

    #net across accounts
    for base in nettedOrders:
        for key in sortedKeys(nettedOrders[base]):pass

    #aggregate across the accounts (e.g. EUR and USD base, their will be a EURUSD aggregation)

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

        accountCCYTotal1 = 0
        for order in accounts.getAccountOrders():
            contraCCy = order.contraCurrency()
            contraAmount = order.contraAmount() if contraCCy=='USD' else convertToMid('USD',contraCCy, order.contraAmount())
            accountCCYTotal1 += contraAmount

        nettedCCYTotal2 = 0
        for base in sortedKeys(netOrders):
            for key in sortedKeys(netOrders[base]):
                order = netOrders[base][key]
                contraAmount = order.contraAmount() if base=='USD' else convertToMid('USD', base, order.contraAmount())
                nettedCCYTotal2 += contraAmount

        print ""
        totalSaved = 0
        for base in netOrders:
            for key in sortedKeys(netOrders[base]):
                order = netOrders[base][key]
                saved = order.getSaving()
                contraCurrency = order.base if order.dealtCurrency == order.term else order.term
                if (contraCurrency != 'USD'):
                    savedUSD = convertToMid('USD', contraCurrency, saved)
                    print "%s (saving %8.2f %s, %8.2f USD)" % (order.__str__(), saved, contraCurrency, savedUSD)
                    saved = savedUSD
                else:
                    pass
                    print "%s (saving %8.2f %s)" % (order.__str__(), saved, contraCurrency)
                totalSaved += saved

        print "\nTotal USD amount saved across the accounts (using individual trades) %.2f" % totalSaved

        print "\nTotal USD amount saved across the accounts (using net account flow) %.2f" % (nettedCCYTotal2 - accountCCYTotal1)


        total += totalSaved
        count += 1
        totals.append(saved)
    print "Average = %f" % (total /count)

    #totals.sort()
    #hist, bin_edges = numpy.histogram(totals, 100)
    #for i in range(0, len(hist)):
    #    print int(bin_edges[i]), hist[i]
    #print totals

