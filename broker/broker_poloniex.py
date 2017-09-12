import poloniex

class Poloniex(object):
    
    def __init__(self, key, secret):
        self.polo = poloniex.Poloniex(key,secret)
    
    def get_balance(self, coin):
        bal = self.polo.returnBalances()

        coin = coin.upper()
        bal = bal[coin]
        
        return float(bal)
    
    def format_pair(self, pair):
        coin, base = pair.split("_")
        
        coin = coin.upper()
        base = base.upper()
        
        return "%s_%s" % (base, coin)
    
    def get_book_amt(self, order_type, pair, rate):
        pair = self.format_pair(pair)
        
        amt_bal = 0
        orders = self.polo.returnOrderBook(pair)  # customize
        
        if order_type == 'a':
            ab = 'asks' # customize
            
        if order_type == 'b':
            ab = 'bids' # customize
        
        for x in orders[ab]:
            # print(x)
            book_rate = float(x[0])
            book_amt = float(x[1])
            
            if (order_type=='a' and book_rate <= rate) or (order_type=='b' and book_rate >= rate):
                amt_bal += book_amt
            else:
                break
        
        return float(amt_bal)
    
    def buy(self, pair, rate, amount):
        pair = self.format_pair(pair)
        return self.polo.buy(pair, rate, amount, "immediateOrCancel")
        
    def sell(self, pair, rate, amount):
        pair = self.format_pair(pair)
        return self.polo.sell(pair, rate, amount, "immediateOrCancel")