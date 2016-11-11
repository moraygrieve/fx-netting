import math

from convention import marketConvention
from prices import getPrice
from orders import FXOrder, Side

class Account:
    def __init__(self, name, base):
        self.name = name
        self.base = base
        self.targets = {}
        self.orders = {}

    def addTarget(self, ccy, ccyAmount, baseAmount):
        self.targets[ccy] = (ccyAmount, baseAmount)
        self.addOrder(ccy, ccyAmount, baseAmount)

    def getName(self): return self.name

    def getBase(self): return self.base

    def getTarget(self, ccy):
        return self.targets[ccy] if self.targets.has_key(ccy) else (0,0)

    def getOrders(self):
        return self.orders

    def addOrder(self, ccy, ccyAmount, baseAmount):
        pair, base, term = marketConvention(ccy, self.base)
        bid, ask = getPrice(pair)
        order = FXOrder()
        order.account = self.name
        order.base = base
        order.term = term
        order.dealtCurrency = ccy
        order.dealtAmount = math.fabs(ccyAmount)
        if ccy == base:
            if ccyAmount > 0:
                order.price = ask
                order.side = Side.BUY
            else:
                order.price = bid
                order.side = Side.SELL
            order.baseAmount = math.fabs(ccyAmount)
            order.termAmount = math.fabs(ccyAmount)
        else:
            if ccyAmount > 0:
                order.price = bid
                order.side = Side.SELL
            else:
                order.price = ask
                order.side = Side.BUY
            order.baseAmount = math.fabs(baseAmount)
            order.termAmount = math.fabs(ccyAmount)
        self.orders[pair]=order


class Accounts:
    def __init__(self, currencies):
        self.accounts = {}
        self.currencies = currencies

    def addAccount(self, name, base):
        account = Account(name, base)
        self.accounts[name] = account
        return account

    def getAccount(self, name):
        if self.accounts.has_key(name): return self.accounts[name]
        return None

    def addAccountTarget(self, name, ccy, ccyAmount, baseAmount):
        if self.accounts.has_key(name): self.accounts[name].addTarget(ccy, ccyAmount, baseAmount)

    def getAccountNames(self):
        names = self.accounts.keys()
        names.sort()
        return names

    def getAccountOrders(self):
        orders = []
        for name in self.getAccountNames():
            accountOrders = self.accounts[name].getOrders()
            keys = accountOrders.keys()
            keys.sort()
            for ccy in keys: orders.append(accountOrders[ccy])
        return orders

    def printAccountTargets(self):
        header = self.__getHeader()
        print "-"*len(header)
        print header
        print "-"*len(header)
        for ccy in self.currencies: print self.__getRow(ccy)
        print "-"*len(header)

    def printAccountOrders(self):
        print ""
        for order in self.getAccountOrders(): print order

    def __getHeader(self):
        header = "| %-5s" % "CCY"
        for name in self.getAccountNames(): header = header + "| %-12s" % name
        return header+"|"

    def __getRow(self, ccy):
        row = "| %-5s" % ccy
        for names in self.getAccountNames():
            row = row + "| %s" % self.__formatRowEntry(self.accounts[names].getTarget(ccy)[0])
        return row+"|"

    def __formatRowEntry(self, value):
        if (value == 0): return "%12s"%"0"
        return ("%12d"%value)
