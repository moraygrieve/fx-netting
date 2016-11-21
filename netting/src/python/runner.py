import random, numpy

from net import Netter
from accounts import Accounts

random.seed(120)
ACCOUNTS = [('Account A','USD'),('Account B','EUR'),('Account C','USD'),('Account D','USD'),('Account E','EUR')]
CURRENCIES = ['AUD','CAD','CHF','GBP','EUR','HKD','JPY','NZD','PLN','USD']

if __name__ == "__main__":
    values = []
    total = 0
    count = 0
    totalFlow = 0
    for i in range(0,10000):
        accounts = Accounts(CURRENCIES)
        accounts.initAccounts(ACCOUNTS)
        flow = accounts.getAccountUSDFlow()
        totalFlow += flow

        netter = Netter(accounts, True)
        saved, netOrders = netter.net()
        if (saved > 0 ):
            values.append((saved/flow)*100.0)
            total += saved
            count += 1

    print "Average saving is %5.2f on a flow of %5.2f" % (total/count, totalFlow/count)
    print "Average percent saving is "
    values.sort()
    hist, bin_edges = numpy.histogram(values, 100)
    for i in range(0, len(hist)):
        print "%5.5f %d" % (bin_edges[i], hist[i])


