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

def getPrice(pair):
    return PRICES.get(pair)

def printPrices():
    pairs = PRICES.keys()
    pairs.sort()
    for pair in pairs:
        if pair == "USDJPY":
            print "%s: %8.2f  %-8.2f" % (pair,PRICES[pair][0],PRICES[pair][1])
        else:
            print "%s: %8.5f  %-8.5f" % (pair,PRICES[pair][0],PRICES[pair][1])
    print
