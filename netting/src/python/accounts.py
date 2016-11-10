class Account:

    def __init__(self, currencies, name, denom):
        self.name = name
        self.denom = denom
        self.targets = {}

    def addTarget(self, ccy, ccyAmount, denomAmount):
        self.targets[ccy] = (ccyAmount, denomAmount)

    def getTarget(self, ccy):
        return self.targets[ccy] if self.targets.has_key(ccy) else (0,0)

class Accounts:
    def __init__(self, currencies):
        self.accounts = {}
        self.currencies = currencies

    def addAccount(self, name, denom):
        account = Account(self.currencies, name, denom)
        self.accounts[name] = account
        return account

    def addAccountTarget(self, name, ccy, ccyAmount, denomAmount):
        if self.accounts.has_key(name): self.accounts[name].addTarget(ccy, ccyAmount, denomAmount)

    def getAccountNames(self):
        names = self.accounts.keys()
        names.sort()
        return names

    def getHeader(self):
        header = "| %-5s" % "CCY"
        for name in self.getAccountNames(): header = header + "| %-12s" % name
        return header+"|"

    def getRow(self, ccy):
        row = "| %-5s" % ccy
        for names in self.getAccountNames():
            row = row + "| %s" % self.formatRowEntry(self.accounts[names].getTarget(ccy)[0])
        return row+"|"

    def formatRowEntry(self, value):
        if (value == 0): return "%12s"%"0"
        return ("%12d"%value)

    def printTarget(self):
        header = self.getHeader()
        print "-"*len(header)
        print header
        print "-"*len(header)
        for ccy in self.currencies: print self.getRow(ccy)
        print "-"*len(header)
