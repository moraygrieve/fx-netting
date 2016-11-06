import os, sys, random

ACCOUNTS = ['Account A','Account B','Account C','Account D']
CURRENCIES = ['AUD','CAD','CHF','CNH','EUR','GBP','HKD','JPY','NZD']

PRICES = {
    'AUDUSD':(0.76689, 0.76705),
    'USDCAD':(1.33698,1.33713),
    'USDCHF':(0.97076,0.97096),
    'USDCNH':(6.76904,6.76954),
    'EURUSD':(1.11184,1.11193),
    'GBPUSD':(1.23465,1.23485),
    'USDHKD':(7.75517,7.75538),
    'USDJPY':(102.61,102.62),
    'NZDUSD':(0.73064,0.73084)
}

def init():
    target = {}
    for ccy in CURRENCIES:
        target[ccy]={}
        for acct in ACCOUNTS:
            r = random.randint(-5,5)
            if (r > 2):
                ccy_amount = 1000000*random.randint(1,10)
                target[ccy][acct]= (ccy_amount,exchange(ccy, ccy_amount))
            elif (r < -2):
                ccy_amount = -1000000*random.randint(1,10)
                target[ccy][acct]= (ccy_amount,exchange(ccy, ccy_amount))
    return target

def exchange(ccy, amount):
    if PRICES.has_key("USD"+ccy):
        bid, ask = PRICES.get("USD"+ccy)
        if (amount>0): return -1 * amount / bid
        else: return -1 * amount / ask
    elif PRICES.has_key(ccy+"USD"):
        bid, ask = PRICES.get(ccy+"USD")
        if (amount>0): return -1 * amount * ask
        else: return -1 * amount * bid

def getHeader():
    header = "| %-8s" % "CCY"
    for act in ACCOUNTS: header = header + "| %-12s" % act + "  %+8s    " % "(USD)"
    return header+"|"

def getRow(ccy, entries):
    row = "| %-8s" % ccy
    for act in ACCOUNTS:
        row = row + "| %s" % formatRowEntry(entries.get(act, (0,0))[0]) + "| %s" % formatRowEntry(entries.get(act, (0,0))[1])
    return row+"|"

def formatRowEntry(value):
    if (value == 0): return "%12s"%"0"
    return ("%12.5d"%value)

def printTarget():
    header = getHeader()
    print "-"*len(header)
    print header
    print "-"*len(header)
    for ccy in CURRENCIES: print getRow(ccy, target[ccy])
    print "-"*len(header)

def printOrders():
    for ccy in CURRENCIES:
        for act in ACCOUNTS:
            amount = target[ccy].get(act,(0,0))
            if PRICES.has_key("USD"+ccy):
                bid, ask = PRICES.get("USD"+ccy)
                if (amount[0] > 0): print "SELL USD%s %f @ %f" % (ccy, amount[1], bid)
                elif (amount[0] < 0): print "BUY  USD%s %f @ %f" % (ccy, amount[1], ask)
            elif PRICES.has_key(ccy+"USD"):
                bid, ask = PRICES.get(ccy+"USD")
                if (amount[0]>0): print "BUY  %sUSD %f @ %f" % (ccy, amount[0], ask)
                elif (amount[0]<0): print "SELL %sUSD %f @ %f" % (ccy, amount[0], bid)

if __name__ == "__main__":
    target = init()
    printTarget()
    printOrders()