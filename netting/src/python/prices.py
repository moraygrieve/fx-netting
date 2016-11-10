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

def getPrice(ccypair):
    return PRICES.get(ccypair)

def printPrices():
    for ccypair in PRICES:
        if ccypair == "USDJPY":
            print "%s: %8.2f  %-8.2f" % (ccypair,PRICES[ccypair][0],PRICES[ccypair][1])
        else:
            print "%s: %8.5f  %-8.5f" % (ccypair,PRICES[ccypair][0],PRICES[ccypair][1])
    print
