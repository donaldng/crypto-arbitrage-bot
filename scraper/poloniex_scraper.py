#!/usr/bin/env python3

from websocket import create_connection
from pymongo import MongoClient
import time
import json
import os

db = MongoClient().arb

ws = create_connection('wss://api2.poloniex.com')
sub = json.dumps({'command': 'subscribe', 'channel': 'BTC_ETH'})
ws.send(sub)

while True:
    try:
        result = json.loads(ws.recv())
        for x in result[2]:
            if x[0] == 'o':
                ts = int(time.time())
                #print(x) # ['o', 1, '0.11601001', '81.81253646'] 0 - asks / sell (higher) 1 - bids / buy (lower)
                # arbitrage oppo = buy is higher than sell.
                data = {'ts':ts, 'd':x[1], 'p':x[2], 'q':x[3], 's':'poloniex'}

                res = db.feed.insert_one(data)
        
    except:
        pass
    
ws.close()