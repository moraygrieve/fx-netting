RANKING = ['EUR','GBP','AUD','NZD','USD','CHF','JPY']
EXCEPTIONS={}

def convention(ccy1,ccy2):
    ccypair = marketConvention(ccy1,ccy2)
    return ccypair,ccypair[0:3],ccypair[3:6]

def marketConvention(ccy1, ccy2):
    if EXCEPTIONS.has_key(ccy1+ccy2): return EXCEPTIONS[ccy1+ccy2]
    if EXCEPTIONS.has_key(ccy2+ccy1): return EXCEPTIONS[ccy2+ccy1]
    r1 = RANKING.index(ccy1) if ccy1 in RANKING else -1
    r2 = RANKING.index(ccy2) if ccy2 in RANKING else -1
    if r1>=0 and r2>=0: return ccy1+ccy2 if r1<r2 else ccy2+ccy1
    if r1>=0: return ccy1+ccy2
    if r2>=0: return ccy2+ccy1

def add(ccypair, ccy1, ccy2):
    EXCEPTIONS[ccy1+ccy2]=ccypair

add("CADCHF","CAD","CHF");
add("CADCZK","CAD","CZK");
add("CADDKK","CAD","DKK");
add("CADHUF","CAD","HUF");
add("CADJPY","CAD","JPY");
add("CADMXN","CAD","MXN");
add("CADNOK","CAD","NOK");
add("CADSEK","CAD","SEK");
add("CADTRY","CAD","TRY");
add("CADZAR","CAD","ZAR");
add("CZKHUF","CZK","HUF");
add("CZKMXN","CZK","MXN");
add("CZKNZD","CZK","NZD");
add("CZKRON","CZK","RON");
add("CZKRUB","CZK","RUB");
add("DKKCZK","DKK","CZK");
add("DKKHUF","DKK","HUF");
add("DKKISK","DKK","ISK");
add("DKKJPY","DKK","JPY");
add("DKKNOK","DKK","NOK");
add("DKKPLN","DKK","PLN");
add("DKKSEK","DKK","SEK");
add("HKDJPY","HKD","JPY");
add("HUFRON","HUF","RON");
add("ISKCZK","ISK","CZK");
add("MTLUSD","MTL","USD");
add("MXNHUF","MXN","HUF");
add("MXNJPY","MXN","JPY");
add("NOKCZK","NOK","CZK");
add("NOKHUF","NOK","HUF");
add("NOKJPY","NOK","JPY");
add("NOKPLN","NOK","PLN");
add("NOKSEK","NOK","SEK");
add("NOKTRY","NOK","TRY");
add("NOKZAR","NOK","ZAR");
add("PLNCZK","PLN","CZK");
add("PLNHUF","PLN","HUF");
add("PLNJPY","PLN","JPY");
add("PLNRON","PLN","RON");
add("PLNRUB","PLN","RUB");
add("PLNTRY","PLN","TRY");
add("RONCZK","RON","CZK");
add("RONHUF","RON","HUF");
add("RONPLN","RON","PLN");
add("RUBHUF","RUB","HUF");
add("SEKCZK","SEK","CZK");
add("SEKHUF","SEK","HUF");
add("SEKJPY","SEK","JPY");
add("SEKPLN","SEK","PLN");
add("SEKRON","SEK","RON");
add("SEKTRY","SEK","TRY");
add("SGDJPY","SGD","JPY");
add("SGDTHB","SGD","THB");
add("THBJPY","THB","JPY");
add("TRYCZK","TRY","CZK");
add("TRYDKK","TRY","DKK");
add("TRYHUF","TRY","HUF");
add("TRYJPY","TRY","JPY");
add("TRYMXN","TRY","MXN");
add("TRYPLN","TRY","PLN");
add("TRYZAR","TRY","ZAR");
add("ZARDKK","ZAR","DKK");
add("ZARJPY","ZAR","JPY");
add("ZARMXN","ZAR","MXN");



