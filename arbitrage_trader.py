import config
import json, time, os
from time import gmtime, strftime, localtime
from pymongo import MongoClient
import importlib


def tweet(msg, to="donaldyann"):
    #t = '@%s %s' % (to, msg)
    #body = {'msg': t}
    #requests.post("http://localhost:8888/tweet", body)
    print(msg)

count=0

db = MongoClient().arb.feed
profit_hist = MongoClient().arb.profit_hist
db.drop()
profit_hist.drop()

pair = "ETH_BTC"

print("%s looking at %s" % (strftime("%Y-%m-%d %H:%M:%S", localtime()), pair))

broker = {}

# Profit
profit_perc = config.expected_margin # 0.5%
dirPath = os.path.dirname(os.path.realpath(__file__))

# Exchange
for x in config.enabled_exchange:
    class_ = getattr(importlib.import_module("broker.broker_%s" % x), "%s" % x.title())
    broker[x] = class_(config.api_info[x]['key'],config.api_info[x]['secret'])

    pid=os.fork()
    if pid==0: # new process
        #print(x)
        ppid = os.getpid()
        os.system("nohup python3 %s/scraper/%s_scraper.py %s >/dev/null 2>&1 &" % (dirPath, x, ppid))
        exit()


while(1):
    time.sleep(1)
    price_info = {}

    # LOOK BACK SECOND
    t = int(time.time())-60
    cur = db.find( { 'ts' : { '$gt' : t } } )
    print('Current data: ', cur.count(), t)
    count+=1
    
    if count > 3:
        # Garbage collector
        db.delete_many( { 'ts' : { '$lt' : t+59 } } )
        count = 0
    
    for x in cur:
        d=x['d']
        p=float(x['p'])
        q=float(x['q'])
        s=x['s']
        #print(x)
        try:
            price_info[s]
        except:
            price_info[s] = {}
        
        if d: # Find MAX bid (buy)
            try:
                if p > price_info[s]['max']['p']: #buy
                    price_info[s]['max']['p'] = p
                    price_info[s]['max']['q'] = q
            except:
                price_info[s]['max'] = {}
                price_info[s]['max']['p'] = p
                price_info[s]['max']['q'] = q
                price_info[s]['max']['f'] = (1.0 - config.fees[s]['sell']) # maker

            
        if not d: # Find MIN ask (sell).
            try:
                if p < price_info[s]['min']['p']:
                    price_info[s]['min']['p'] = p
                    price_info[s]['min']['q'] = q
            except:
                price_info[s]['min'] = {}
                price_info[s]['min']['p'] = p
                price_info[s]['min']['q'] = q
                price_info[s]['min']['f'] = (1.0 + config.fees[s]['buy']) # taker
    
    
    # if MAX bid is greater than MIN ask. Check for arbitrage opportunity.
    if len(price_info) > 1:
        for b1, l1 in price_info.items():
            for b2, l2 in price_info.items():
                if b1 != b2:
                    cur_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
                    
                    try:
                        l1_max = l1['max']['p']*l1['max']['f']
                        l1_max_o = l1['max']['p']
                        l2_min = l2['min']['p']*l2['min']['f']
                        l2_min_o = l2['min']['p']                        
                        if l1_max > l2_min:
                            arb_perc = round(((l1_max/l2_min)-1)*100, 2)
                            if arb_perc > profit_perc:
                                print('%s %s arbitrage gap %s%%' % (cur_time,arb_perc))
                                #tweet('%s %s arbitrage gap %s%%' % (cur_time,arb_perc))
                                # broker['bitfinex'].buy(pair, 123, 1)
                                # broker['bitfinex'].sell(pair, 123, 1)
                                time.sleep(60)
                    except:
                        pass
                    
                    try:
                        l2_max = l2['max']['p']*l2['max']['f']
                        l2_max_o = l2['max']['p']
                        
                        l1_min = l1['min']['p']*l1['min']['f']
                        l1_min_o = l1['min']['p']  
                        if l2_max > l1_min:
                            arb_perc = round(((l2_max/l1_min)-1)*100, 2)
                            if arb_perc > profit_perc:  
                                print('%s %s arbitrage gap %s%%' % (cur_time,arb_perc))
                                #tweet('%s %s arbitrage gap %s%%' % (cur_time,arb_perc))
                                # broker['bitfinex'].buy(pair, 123, 1)
                                # broker['bitfinex'].sell(pair, 123, 1)                                
                                time.sleep(60)
                    except:
                        pass
