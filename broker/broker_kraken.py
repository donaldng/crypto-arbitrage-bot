import krakenex

class Kraken(object):
    
    def __init__(self, key, secret):
        self.kraken = krakenex.API(key,secret)
    
    def get_balance(self, coin):
        bal = self.kraken.query_private('Balance')['result']

        coin = coin.upper()
        
        if coin == 'BTC':
            coin = 'XXBT'
        elif coin == 'USD':
            coin = 'ZUSD'
        else:
            coin = 'X%s' % coin

        bal = bal[coin]
            
        return float(bal)
    
    def format_pair(self, pair):
        coin, base = pair.split("_")
        
        coin = coin.upper()
        base = base.upper()
        
        if coin == 'BTC':
            coin = 'XXBT'
        elif coin == 'USD':
            coin = 'ZUSD'
        else:
            coin = 'X%s' % coin        

        if base == 'BTC':
            base = 'XXBT'
        elif base == 'USD':
            base = 'ZUSD'
        else:
            base = 'X%s' % base                 
            
        return "%s%s" % (coin, base)
    
    def get_book_amt(self, order_type, pair, rate):
        pair = self.format_pair(pair)

        amt_bal = 0
        res = self.kraken.query_public('Depth',{'pair': pair, 'count': '10'})['result']  # customize
        
        if order_type == 'a':
            ab = 'asks' # customize
            
        if order_type == 'b':
            ab = 'bids' # customize
        
        for k_pair, orders in res.items():
            
            for x in orders[ab]:
                book_rate = float(x[0])
                book_amt = float(x[1])
                
                if (order_type=='a' and book_rate <= rate) or (order_type=='b' and book_rate >= rate):
                    amt_bal += book_amt
                else:
                    pass # break
        
        return float(amt_bal)
    
    def buy(self, pair, rate, amount):
        pair = self.format_pair(pair)
        req_data = {'pair': pair, 'type': 'buy', 'ordertype': 'limit', 'price': rate, 'volume': amount, 'expiretm': '+10'}
        return self.kraken.query_private('AddOrder', req_data)
        
    def sell(self, pair, rate, amount):
        pair = self.format_pair(pair)
        req_data = {'pair': pair, 'type': 'sell', 'ordertype': 'limit', 'price': rate, 'volume': amount, 'expiretm': '+10'}
        return self.kraken.query_private('AddOrder', req_data)