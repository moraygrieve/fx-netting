import random, math, copy, numpy

random.seed(24)

#constants for the run
ACCOUNTS = ['Account A','Account B','Account C','Account D']
CURRENCIES = ['AUD','CAD','CHF','CNH','EUR','GBP','HKD','JPY','NZD','PLN']
PRICES = {
    'AUDUSD':(0.76689, 0.76705),
    'USDCAD':(1.33698,1.33713),
    'USDCHF':(0.97076,0.97096),
    'USDCNH':(6.76904,6.76954),
    'EURUSD':(1.11184,1.11193),
    'GBPUSD':(1.23465,1.23485),
    'USDHKD':(7.75517,7.75538),
    'USDJPY':(102.61,102.62),
    'NZDUSD':(0.73064,0.73084),
    'USDPLN':(3.89141, 3.89354)
}

#data structures
class FXOrder:
    def __init__(self):
        self.account = ""
        self.base = ""
        self.term = ""
        self.side = ""
        self.price = 0.0
        self.baseAmount = 0
        self.termAmount = 0
        self.dealtCurrency = ""
        self.dealtAmount = 0

    def isBuy(self):
        return self.side == "BUY "

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
        fstring = "[%-10s] %s  %s%s  %12.2f @ %-10.5f (%-10d dealt %s)"
        if self.dealtCurrency == 'JPY': fstring = "[%-10s] %s  %s%s  %12.2f @ %-10.2f (%-10d dealt %s)"
        return fstring % \
               (self.account, self.side, self.base, self.term, self.baseAmount, self.price, self.dealtAmount, self.dealtCurrency)

def initAccounts():
    """Populate the target positions randomly.
    """
    target = {}  #map< currency, map<account, (ccy, usd)> >
    orders = {}  #map< account, map<currency, order> >
    for ccy in CURRENCIES:
        target[ccy]={}
        for acct in ACCOUNTS:
            r = random.randint(-5,5)
            if (r > 2): ccy_amount = convertFromUSDMid(ccy, 1000000*random.randint(1,10))
            elif (r < -2): ccy_amount = convertFromUSDMid(ccy, -1000000*random.randint(1,10))
            else: continue
            if ccy_amount == 0: continue
            usd_amount = convertToUSD(ccy, ccy_amount)
            target[ccy][acct]= (ccy_amount, usd_amount)

            order = FXOrder()
            order.account = acct
            order.dealtCurrency = ccy
            order.dealtAmount = math.fabs(ccy_amount)
            if isCcyBase(ccy):
                order.base = ccy
                order.term = "USD"
                bid, ask = PRICES.get(ccy+"USD", (0,0))
                if ccy_amount > 0:
                    order.price = ask
                    order.side = "BUY "
                else:
                    order.price = bid
                    order.side = "SELL"
                order.baseAmount = math.fabs(ccy_amount)
                order.termAmount = math.fabs(usd_amount)
            else:
                order.base = "USD"
                order.term = ccy
                bid, ask = PRICES.get("USD"+ccy, (0,0))
                if ccy_amount > 0:
                    order.price = bid
                    order.side = "SELL"
                else:
                    order.price = ask
                    order.side = "BUY "
                order.baseAmount = math.fabs(usd_amount)
                order.termAmount = math.fabs(ccy_amount)
            if not orders.has_key(acct): orders[acct]={}
            orders[acct][order.base+order.term]=order
    return target, orders

def isCcyBase(ccy):
    """Return true if this currency is base in conventional notation
    """
    if PRICES.has_key("USD"+ccy): return False
    return True

def roundup(amount):
    """Roundup to the nearest million.
    """
    return int(math.ceil(amount/1000000.0)) * 1000000


def convertFromUSDMid(ccy, amount):
    """Convert from USD to target currency, using mid price.
    """
    if PRICES.has_key("USD"+ccy):
        bid, ask = PRICES.get("USD"+ccy)
        return roundup(amount * ((bid + ask)/2))
    elif PRICES.has_key(ccy+"USD"):
        bid, ask = PRICES.get(ccy+"USD")
        return roundup(amount / ((bid + ask)/2))


def convertToUSD(ccy, amount):
    """Convert to USD from target currency, using bid or ask.
    """
    if PRICES.has_key("USD"+ccy):
        bid, ask = PRICES.get("USD"+ccy)
        if (amount>0): return -1 * amount / bid
        else: return -1 * amount / ask
    elif PRICES.has_key(ccy+"USD"):
        bid, ask = PRICES.get(ccy+"USD")
        if (amount>0): return -1 * amount * ask
        else: return -1 * amount * bid

def printPrices():
    for ccypair in PRICES:
        if ccypair == "USDJPY":
            print "%s: %8.2f  %-8.2f" % (ccypair,PRICES[ccypair][0],PRICES[ccypair][1])
        else:
            print "%s: %8.5f  %-8.5f" % (ccypair,PRICES[ccypair][0],PRICES[ccypair][1])
    print

def getHeader():
    header = "| %-5s" % "CCY"
    for act in ACCOUNTS: header = header + "| %-12s" % act
    return header+"|"


def getRow(ccy, entries):
    row = "| %-5s" % ccy
    for act in ACCOUNTS:
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
        for act in ACCOUNTS:
            if not orders.has_key(act): continue
            for ccy in CURRENCIES:
                ccypair = ccy+"USD" if isCcyBase(ccy) else "USD"+ccy
                if not orders[act].has_key(ccypair): continue
                print orders[act][ccypair]


def getTotals(orders):
    netted = {} #map<currency, (BUY, SELL)>
    netOrders = []
    for ccy in CURRENCIES:
        ccypair = ccy+"USD" if isCcyBase(ccy) else "USD"+ccy
        for act in ACCOUNTS:
            if orders.has_key(act) and orders[act].has_key(ccypair):
                if not netted.has_key(ccypair):
                    buy = FXOrder()
                    buy.account = "Netted"
                    buy.side = "BUY "
                    buy.dealtCurrency = ccy

                    sell = FXOrder()
                    sell.account = "Netted"
                    sell.side = "SELL"
                    sell.dealtCurrency = ccy

                    if isCcyBase(ccy):
                        buy.base = ccy
                        buy.term = "USD"
                        sell.base = ccy
                        sell.term = "USD"
                    else:
                        buy.base = "USD"
                        buy.term = ccy
                        sell.base = "USD"
                        sell.term = ccy
                    netted[ccypair] = (buy, sell)

                order = orders[act][ccypair]
                if order.isBuy():netted[ccypair][0].include(order)
                else: netted[ccypair][1].include(order)

    print ""
    totalSaved = 0
    for ccy in CURRENCIES:
        ccypair = ccy+"USD" if isCcyBase(ccy) else "USD"+ccy
        bid, ask = PRICES.get(ccypair)
        if netted.has_key(ccypair):
            #net out the dealt amount
            buyAmount = netted[ccypair][0].dealtAmount
            sellAmount = netted[ccypair][1].dealtAmount
            order = FXOrder()
            order.account = "Netted"
            order.dealtCurrency = ccy

            if (buyAmount >= sellAmount):
                order.side = "BUY "
                order.price = ask
                order.dealtAmount = netted[ccypair][0].dealtAmount - netted[ccypair][1].dealtAmount

                dealtSaved = netted[ccypair][1].dealtAmount
                if isCcyBase(ccy):
                    order.base = ccy
                    order.term = "USD"
                    order.baseAmount = order.dealtAmount
                    order.termAmount = order.dealtAmount * order.price
                    saving = dealtSaved*ask - dealtSaved*bid
                else:
                    order.base = "USD"
                    order.term = ccy
                    order.baseAmount = order.dealtAmount / order.price
                    order.termAmount = order.dealtAmount
                    saving = dealtSaved/bid - dealtSaved/ask

            else:
                order.side = "SELL"
                order.price = bid
                order.dealtAmount = netted[ccypair][1].dealtAmount - netted[ccypair][0].dealtAmount

                dealtSaved = netted[ccypair][0].dealtAmount
                if isCcyBase(ccy):
                    order.base = ccy
                    order.term = "USD"
                    order.baseAmount = order.dealtAmount
                    order.termAmount = order.dealtAmount * order.price
                    saving = dealtSaved*ask - dealtSaved*bid
                else:
                    order.base = "USD"
                    order.term = ccy
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

#the entry point
if __name__ == "__main__":
    total = 0
    count = 0
    totals = []
    for i in range(0,1):
        target, rawOrders = initAccounts()
        printPrices()
        printTarget(target)
        printOrders(rawOrders)
        saved, netOrders = getTotals(rawOrders)

        total += saved
        count += 1
        totals.append(saved)
    print "Average = %f" % (total /count)

    #totals.sort()
    #hist, bin_edges = numpy.histogram(totals, 100)
    #for i in range(0, len(hist)):
    #    print int(bin_edges[i]), hist[i]

    #print totals
