import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

class Oanda:

    def __init__(self,access_token):
        self.access_token = access_token

        self.default_headers = {'Content-Type': 'application/json',
           'Authorization': f'Bearer {self.access_token}'}

        self.default_params = {'instruments': 'EUR_USD,USD_JPY'}

        self.account_endpoint = 'https://api-fxpractice.oanda.com/v3/accounts'

        self.instruments_endpoint = 'https://api-fxpractice.oanda.com/v3/instruments'

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
    
    def partialClosePosition(self, instrument, units):

        data = {}
        if units < 0:
            units = abs(units)
            data = {
                "shortUnits": str(units)
            }
        else:
            data = {
                "longUnits": str(units)
            }


        endpoint = self.account_endpoint + self.account_id + '/positions' + "/" + instrument + "/close"
        response = requests.put(endpoint, headers=self.default_headers, data=json.dumps(data))

        if response.status_code != 200:
            raise Exception("Could not close position partially.")

        return response.json()

        
oanda = Oanda(os.getenv("ACCESS_TOKEN"))

oanda.setCurrentAccount('101-001-24797201-001')


# what price level do you want the trade to close at
partialcloseprice = 148.727

test = 'hello'

# how many units do you want to partially close 
partialcloseunits = 63282

# long or short position
position = "long"

# what pair are you trading 
instrument = "EUR_JPY"

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
        breakevenprice = theposition["long"]["averagePrice"]

breakevenprice = float(breakevenprice)


if position == "long":

    while True:

        print("Long loop running.")

        # check price of candles 
        candle = oanda.getCandles(timeframe, 1 ,instrument)
        recentcandleprice = candle['candles'][0]['mid']['o']
        print(recentcandleprice)

        # if recent candle price > partial close price
        if float(recentcandleprice) > partialcloseprice:

            print("Price has crossed the alert.")


            #close partially
            oanda.partialClosePosition(instrument, partialcloseunits)

            # set stop loss to breakeven
            oanda.replaceOrder(tradeid, breakevenprice)
            
            break

        # wait 1 minute to run command again 
        time.sleep(60)
elif position == "short":

    print("Short loop running.")
    while True:

        # check price of candles 
        candle = oanda.getCandles(timeframe, 1 ,instrument)
        recentcandleprice = candle['candles'][0]['mid']['o']

        # if recent candle price < partial close price
        if recentcandleprice < partialcloseprice:

            print("Price has crossed the alert.")

            #close partially
            oanda.partialClosePosition(instrument, -partialcloseunits)

            # set stop loss to breakeven
            oanda.replaceOrder(tradeid, breakevenprice)
            
            break

        # wait 1 minute to run command again 
        time.sleep(60)



