import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

class Oanda:

    def __init__(self, access_token, is_demo=True):
        self.access_token = access_token
        self.is_demo = is_demo

        self.default_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        self.default_params = {'instruments': 'EUR_USD,USD_JPY'}

        # Determine endpoints based on the is_demo flag
        if self.is_demo:
            self.base_url = 'https://api-fxpractice.oanda.com/v3'
        else:
            self.base_url = 'https://api-fxtrade.oanda.com/v3'

        self.account_endpoint = f'{self.base_url}/accounts'
        self.instruments_endpoint = f'{self.base_url}/instruments'

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


    def getAllOrders(self, currency_pair=None, allpairs=True):
        endpoint = self.account_endpoint + self.account_id + '/orders'

        params = {}
        if not allpairs and currency_pair is not None:
            params['instrument'] = currency_pair

        response = requests.get(endpoint, headers=self.default_headers, params=params)

        if response.status_code != 200:
            raise Exception("Could not fetch all orders.")

        return response.json()
    
    
    def replaceOrder(self, tradeid, price,type="STOP_LOSS",timeInForce="GTC", orderspecify="StopLossOrderRequest"):

        #orderspecify = order id

        data = {
        "order": {
            #"timeinForce": timeInForce,
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
    