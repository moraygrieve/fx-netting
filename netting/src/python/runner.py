import random, numpy

from net import Netter
from accounts import Accounts

random.seed(120)
ACCOUNTS = [('Account A','USD'),('Account B','EUR'),('Account C','USD'),('Account D','USD'),('Account E','EUR')]
CURRENCIES = ['AUD','CAD','CHF','GBP','EUR','HKD','JPY','NZD','PLN','USD']

if __name__ == "__main__":
    values = []
    count = 0
    totalSpread = 0
    totalSaving = 0
    for i in range(0,10000):
        accounts = Accounts(CURRENCIES)
        accounts.initAccounts(ACCOUNTS)
        spread = accounts.getSpreadCost()
        totalSpread += spread

        netter = Netter(accounts, True)
        saved, netOrders = netter.net()
        if (saved > 0 ):
            values.append((saved/spread)*100.0)
            totalSaving += saved
            count += 1

    print "Average saving is %5.2f on a flow of %5.2f" % (totalSaving/count, totalSpread/count)
    print "Average percent saving is %5.2f" % (totalSaving / totalSpread)
    values.sort()
    hist, bin_edges = numpy.histogram(values, 40)
    for i in range(0, len(hist)):
        print "%5.2f %d" % (bin_edges[i], hist[i])


