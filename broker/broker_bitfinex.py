from broker.client import TradeClient, Client

class Bitfinex(object):
    
    def __init__(self, key, secret):
        self.bfx = TradeClient(key,secret)
        self.client = Client()
        
    def get_balance(self, coin):
        bal = self.bfx.balances()

        coin = coin.upper()
        for x in bal:
            if x['currency'] == coin:
                bal = x['available']
                break
            
        return float(bal)
    
    def format_pair(self, pair):
        coin, base = pair.split("_")
        return "%s%s" % (coin.lower(), base.lower())
    
    def get_book_amt(self, order_type, pair, rate):
        pair = self.format_pair(pair)

        amt_bal = 0
        orders = self.client.order_book(pair)  # customize
        
        if order_type == 'a':
            ab = 'asks' # customize
            
        if order_type == 'b':
            ab = 'bids' # customize
        
        for x in orders[ab]:
            #print(x)
            book_rate = float(x['price'])
            book_amt = float(x['amount'])

            if (order_type=='a' and rate >= book_rate) or (order_type=='b' and book_rate >= rate):
                amt_bal += book_amt
            else:
                break
        
        return float(amt_bal)

        
        
    def buy(self, pair, rate, amount):
        pair = self.format_pair(pair)
        return self.bfx.place_order(self, amount, rate, "buy", "exchange market", pair)
        
    def sell(self, pair, rate, amount):
        pair = self.format_pair(pair)
        return self.bfx.place_order(self, amount, rate, "sell", "exchange market", pair)
        
    '''
    Either “market” / “limit” / “stop” / “trailing-stop” / “fill-or-kill” / “exchange market” / “exchange limit” / “exchange stop” / “exchange trailing-stop” / “exchange fill-or-kill”. (type starting by “exchange ” are exchange orders, others are margin trading orders)
    '''    
