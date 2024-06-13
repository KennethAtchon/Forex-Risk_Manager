import requests
import json
import os
import time

class Oanda:

    def __init__(self,access_token):
        self.access_token = access_token

        self.default_headers = {'Content-Type': 'application/json',
           'Authorization': f'Bearer {self.access_token}'}

        self.default_params = {'instruments': 'EUR_USD,USD_JPY'}

        # fxpractice -> fxtrade if live
        self.account_endpoint = 'https://api-fxtrade.oanda.com/v3/accounts'

        self.instruments_endpoint = 'https://api-fxtrade.oanda.com/v3/instruments'

        self.account_id = ''

    def getAllAccounts(self):

        response = requests.get(self.account_endpoint, headers=self.default_headers)
        return response.json()
    
    def setCurrentAccount(self, current_id):
        self.account_id = '/' + current_id

        response = requests.get(self.account_endpoint + self.account_id, headers= self.default_headers, params=self.default_params )

        response = response.json()
        
        if 'errorMessage' in response:
            raise Exception("You have entered the wrong account_id")

    def getAccountSummary(self):
        if self.account_id == '':
            print("Account ID has not been set.")
            return ''
        
        response = requests.get(self.account_endpoint + self.account_id + '/summary', headers=self.default_headers)
        return response.json()

    def getCandles(self, timeframe, count, currency_pair):
        # timeframe format: H5 (4 hours) S5(5 seconds)

        get_candles = self.instruments_endpoint + "/" + currency_pair + "/candles"

        params = {'granularity': timeframe, 'count': count}

        response = requests.get(get_candles, headers=self.default_headers, params=params)

        if 'errorMessage' in response:
            raise Exception("Something went wrong with retrieving candles.")

        return response.json()


    def getAllOrders(self, curreny_pair):
        endpoint = self.account_endpoint + self.account_id + '/orders'

        params = { "instrument": curreny_pair}
        response = requests.get(endpoint, headers=self.default_headers, params= params)

        if response.status_code != 200:
            raise Exception("Could not fetch all orders.")

        return response.json()
    
    
    def replaceOrder(self, tradeid, price,type="STOP_LOSS",timeInForce="GTC", orderspecify="StopLossOrderRequest"):

        data = {
        "order": {
            "timeinForce": timeInForce,
            "price": price,
            "type": type,
            "tradeID": tradeid
            }
        }

        endpoint = self.account_endpoint + self.account_id + '/orders' + "/" + orderspecify
        response = requests.put(endpoint, headers=self.default_headers, data=json.dumps(data))

        if response.status_code != 201:
            raise Exception("Could replace order.")

        return response.json()
    
    def getAllPositions(self):
        endpoint = self.account_endpoint + self.account_id + '/openPositions'
        response = requests.get(endpoint, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception("Could not fetch all positions.")

        return response.json()
    

def runProgram(position, instrument, move_price, timeframe,breakevenprice, usebreakeven=False):


    while True:

        # check price of candles 
        candle = oanda.getCandles(timeframe, 1 ,instrument)
        recentcandleprice = candle['candles'][0]['mid']['o']
        print(recentcandleprice)
        recentcandleprice = float(recentcandleprice)

        if position == "long":
            if usebreakeven:
                if recentcandleprice > breakevenprice:
                    # set stop loss to breakeven
                    oanda.replaceOrder(tradeid, breakevenprice)
                    
                    break
            else:
                if recentcandleprice > move_price:
                    # set stop loss to breakeven
                    oanda.replaceOrder(tradeid, breakevenprice)
                    
                    break

        if position == "short":
            if usebreakeven:
                if recentcandleprice < breakevenprice:
                    # set stop loss to breakeven
                    oanda.replaceOrder(tradeid, breakevenprice)
                    
                    break
            else:
                if recentcandleprice < move_price:
                    # set stop loss to breakeven
                    oanda.replaceOrder(tradeid, breakevenprice)
                    
                    break

        # wait 1 minute to run command again 
        time.sleep(15)



oanda = Oanda(os.getenv("ACCESS_TOKEN"))

oanda.setCurrentAccount('001-001-9634241-002')

# not need if automatic breakeven
move_price = 1.08220

# long or short position
position = "short"

# what pair are you trading 
instrument = "EUR_USD"

# timeframe format: H5 (4 hours) S5(5 seconds) M15( 15 minutes)
# Note: this just changes when your getting out, ex: on the 1m could pass ur
# alert but on 1h it doesn't register a new candle in that timeframe
timeframe = "M1"

# You dont have to set these fields below

#trade id
# assuming you have 1 position per pair
orders = oanda.getAllOrders(instrument)

# look at the type of the order
#print(orders)

tradeid = ""

if orders['orders'][0]['type'] == "STOP_LOSS":
    tradeid = orders['orders'][0]['id']
else:
    tradeid = orders['orders'][1]['id']


# breakeven price
positions = oanda.getAllPositions()

#print(positions)

breakevenprice = ""

for theposition in positions['positions']:
    if theposition['instrument'] == instrument:
        breakevenprice = theposition[position]["averagePrice"]



breakevenprice = float(breakevenprice)

runProgram(position, instrument, move_price, timeframe, breakevenprice, usebreakeven=True)

