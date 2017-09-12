#!/usr/bin/env python3

from pymongo import MongoClient
import os, requests, json, time, sys

db = MongoClient().arb

pid = int(sys.argv[1]) if len(sys.argv) != 1 else 0

while True:

    os.system("clear")
    print("Bitfinex running... --%s" % (str(time.time())[-3:]))

    try:
        os.kill(pid, 0)
    except:  # Probably ENOSUCH
        sys.exit()
        
    try:
        data = requests.get("https://api.bitfinex.com/v1/book/ethbtc?group=1").json()
        for types, order in data.items():
            
            d = 0

            if types == "bids":
                d = 1

            for x in order:
                ts = int(float(x['timestamp']))
                
                data = {'ts':ts, 'd':d, 'p':float(x['price']), 'q':abs(float(x['amount'])), 's':'bitfinex'}

                res = db.feed.insert_one(data)
        
        time.sleep(1.5)
    except:
        pass
