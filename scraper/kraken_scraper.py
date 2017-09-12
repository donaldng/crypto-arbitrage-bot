#!/usr/bin/env python3

from pymongo import MongoClient
import time
from time import gmtime, strftime, localtime
import json
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import krakenex

db = MongoClient().arb
k = krakenex.API(config.api_info['kraken']['key'],config.api_info['kraken']['secret'])
pid = int(sys.argv[1]) if len(sys.argv) != 1 else 0

while(1):
    os.system("clear")
    print("Kraken running... --%s" % (str(time.time())[-3:]))

    try:
        os.kill(pid, 0)
    except:  # Probably ENOSUCH
        sys.exit()

    try:
        res = k.query_public('Depth',{'pair': 'ETHXBT', 'count': '10'})['result']
        for k_pair, orders in res.items():
            for askbid, list in orders.items():
                # 0 - asks / sell (higher) 1 - bids / buy (lower)
                
                d = 0 if askbid=='asks' else 1
                
                for x in list:
                    ts = int(x[2])
                    p = x[0]
                    q = x[1]
                    
                    if ts >= int(time.time())-4:
                        data = {'ts':ts, 'd':d, 'p':p, 'q':q, 's':'kraken'}
                        r = db.feed.insert_one(data)
        print("%s OK" % strftime("%Y-%m-%d %H:%M:%S", localtime()))
    except:
        print('error')

    time.sleep(3)