import os, sys, random

ACCOUNTS = ['Account A','Account B','Account C','Account D']
CURRENCIES = ['AUD','CAD','CHF','CNH','EUR','GBP','HKD','JPY','NZD']

PRICES = {
    'AUDUSD':(0.76689, 0.76705),
    'EURUSD':(1.11184,1.11193),
    'GBPUSD':(1.23465,1.23485),
    'NZDUSD':(0.73064,0.73084),
    'USDCAD':(1.33698,1.33713),
    'USDCHF':(0.97076,0.97096),
    'USDCNH':(6.76904,6.76954),
    'USDHKD':(7.75517,7.75538),
    'USDJPY':(102.61,102.62)
}

def init():
    target = {}
    for ccy in CURRENCIES:
        target[ccy]={}
        for acct in ACCOUNTS:
            r = random.randint(-5,5)
            if (r > 2): target[ccy][acct]= 1000000*random.randint(1,25)
            elif (r < -2): target[ccy][acct]= -1000000*random.randint(1,25)
    return target

def getHeader():
    header = "| %-12s " % "CCY"
    for act in ACCOUNTS: header += "| %-12s" % act
    return header+"|"

def getRow(ccy, entries):
    row = "| %-12s " % ccy
    for act in ACCOUNTS: row += "| %+12s" % entries.get(act, 0)
    return row+"|"

def printTarget():
    header = getHeader()
    print "-"*len(header)
    print header
    print "-"*len(header)
    for ccy in CURRENCIES: print getRow(ccy, target[ccy])
    print "-"*len(header)

if __name__ == "__main__":
    target = init()
    printTarget()