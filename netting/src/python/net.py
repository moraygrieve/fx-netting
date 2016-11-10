import random, math
from convention import marketConvention
from orders import FXOrder, AccountOrders
from prices import getPrice, printPrices

random.seed(24)
ACCOUNTS = [('Account A','USD'),('Account B','USD'),('Account C','USD'),('Account D','USD')]
CURRENCIES = ['AUD','CAD','CHF','CNH','EUR','GBP','HKD','JPY','NZD','PLN']

def initAccounts():
    target = {}
    orders = AccountOrders()
    for ccy in CURRENCIES:
        target[ccy]={}

        for acct,denom in ACCOUNTS:
            r = random.randint(-5,5)
            if (r > 2): ccy_amount = convertFromDenomMid(ccy, denom, 1000000*random.randint(1,10))
            elif (r < -2): ccy_amount = convertFromDenomMid(ccy, denom, -1000000*random.randint(1,10))
            else: continue
            if ccy_amount == 0: continue
            contra_amount = convertToDenom(ccy, denom, ccy_amount)
            target[ccy][acct]= (ccy_amount, contra_amount)
            orders.addToAccount(acct, denom, ccy, ccy_amount, contra_amount)
    return target, orders

def roundup(amount):
    return int(math.ceil(amount/1000000.0)) * 1000000

def convertFromDenomMid(ccy, denom, amount):
    ccypair,base,term = marketConvention(ccy,denom)
    bid,ask = getPrice(ccypair)
    if ccy == term:
        return roundup(amount * ((bid + ask)/2))
    elif ccy == base:
        return roundup(amount / ((bid + ask)/2))

def convertToDenom(ccy, denom, amount):
    ccypair,base,term = marketConvention(ccy,denom)
    bid,ask = getPrice(ccypair)
    if ccy == term:
        if (amount>0): return -1 * amount / bid
        else: return -1 * amount / ask
    elif ccy == base:
        if (amount>0): return -1 * amount * ask
        else: return -1 * amount * bid

def getHeader():
    header = "| %-5s" % "CCY"
    for act,denom in ACCOUNTS: header = header + "| %-12s" % act
    return header+"|"

def getRow(ccy, entries):
    row = "| %-5s" % ccy
    for act,denom in ACCOUNTS:
        row = row + "| %s" % formatRowEntry(entries.get(act, (0,0))[0])
    return row+"|"

def formatRowEntry(value):
    if (value == 0): return "%12s"%"0"
    return ("%12d"%value)

def printTarget(target):
    header = getHeader()
    print "-"*len(header)
    print header
    print "-"*len(header)
    for ccy in CURRENCIES: print getRow(ccy, target[ccy])
    print "-"*len(header)

def printOrders(orders):
        print ""
        for act,denom in ACCOUNTS:
            if not orders.has_key(act): continue
            for ccy in CURRENCIES:
                ccypair,base,term = marketConvention(ccy,denom)
                if not orders[act].has_key(ccypair): continue
                print orders[act][ccypair]

def getTotals(orders):
    netted = {} #map<currency, (BUY, SELL)>
    netOrders = []
    for ccy in CURRENCIES:

        for act,denom in ACCOUNTS:
            ccypair,base,term = marketConvention(ccy,denom)

            if orders.has_key(act) and orders[act].has_key(ccypair):
                if not netted.has_key(ccypair):
                    buy = FXOrder()
                    buy.account = "Netted"
                    buy.base = base
                    buy.term = term
                    buy.side = "BUY "
                    buy.dealtCurrency = ccy

                    sell = FXOrder()
                    sell.account = "Netted"
                    sell.base = base
                    sell.term = term
                    sell.side = "SELL"
                    sell.dealtCurrency = ccy
                    netted[ccypair] = (buy, sell)

                order = orders[act][ccypair]
                if order.isBuy():netted[ccypair][0].include(order)
                else: netted[ccypair][1].include(order)

    print ""
    totalSaved = 0
    for ccy in CURRENCIES:
        ccypair,base,term = marketConvention(ccy,denom)
        bid, ask = getPrice(ccypair)

        if netted.has_key(ccypair):
            buyAmount = netted[ccypair][0].dealtAmount
            sellAmount = netted[ccypair][1].dealtAmount
            order = FXOrder()
            order.account = "Netted"
            order.base = base
            order.term = term
            order.dealtCurrency = ccy

            if (buyAmount >= sellAmount):
                order.side = "BUY "
                order.price = ask
                order.dealtAmount = netted[ccypair][0].dealtAmount - netted[ccypair][1].dealtAmount

                dealtSaved = netted[ccypair][1].dealtAmount
                if ccy == base:
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
                order.dealtAmount = netted[ccypair][1].dealtAmount - netted[ccypair][0].dealtAmount

                dealtSaved = netted[ccypair][0].dealtAmount
                if ccy == base:
                    order.baseAmount = order.dealtAmount
                    order.termAmount = order.dealtAmount * order.price
                    saving = dealtSaved*ask - dealtSaved*bid
                else:
                    order.baseAmount = order.dealtAmount / order.price
                    order.termAmount = order.dealtAmount
                    saving = dealtSaved/bid - dealtSaved/ask

            totalSaved += saving

            #print netted[ccypair][0]
            #print netted[ccypair][1]
            if (order.baseAmount > 0):
                netOrders.append(order)
                fstring = "%s - saving %.2f USD"
                print fstring % (order.__str__(), saving)
    print "\nTotal USD amount saved across the accounts %.2f" % totalSaved
    return totalSaved, netOrders

if __name__ == "__main__":
    total = 0
    count = 0
    totals = []
    for i in range(0,1):
        target, rawOrders = initAccounts()
        printPrices()
        printTarget(target)
        printOrders(rawOrders.orders)
        saved, netOrders = getTotals(rawOrders.orders)

        total += saved
        count += 1
        totals.append(saved)
    print "Average = %f" % (total /count)

    #totals.sort()
    #hist, bin_edges = numpy.histogram(totals, 100)
    #for i in range(0, len(hist)):
    #    print int(bin_edges[i]), hist[i]

    #print totals

