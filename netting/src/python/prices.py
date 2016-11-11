PRICES = {
    'AUDUSD':(0.76689, 0.76705),
    'USDCAD':(1.33698,1.33713),
    'USDCHF':(0.97076,0.97096),
    'USDCNH':(6.76904,6.76954),
    'GBPUSD':(1.23465,1.23485),
    'USDHKD':(7.75517,7.75538),
    'USDJPY':(102.61,102.62),
    'NZDUSD':(0.73064,0.73084),
    'USDPLN':(3.89141, 3.89354),
    'EURAUD':(1.44951,1.44992),
    'EURCAD':(1.48651,1.48677),
    'EURCHF':(1.07939,1.07959),
    'EURHKD':(8.62258,8.62335),
    'EURGBP':(0.90043,0.90055),
    'EURJPY':(114.09,114.104),
    'EURNZD':(1.52134,1.52184),
    'EURPLN':(4.32701,4.32897),
    'EURUSD':(1.11184,1.11193)
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