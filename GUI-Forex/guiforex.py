import customtkinter
import requests
import json
import os
import time


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("640x800")
root.title("Forex Risk Manager")

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

program_running = True



def runProgram():

    oanda = Oanda(access_Token.get())

    oanda.setCurrentAccount(accountId.get())    

    partialcloseprice = partialcloseprice_.get()

    partialcloseunits = partialcloseunits_.get()

    position = position_.get()

    instrument = instrument_.get()

    timeframe = timeframe_.get()

    orders = oanda.getAllOrders(instrument)
    tradeid = ""

    if orders['orders'][0]['type'] == "STOP_LOSS":
        tradeid = orders['orders'][0]['id']
    else:
        tradeid = orders['orders'][1]['id']

    positions = oanda.getAllPositions()

    breakevenprice = ""

    for theposition in positions['positions']:
        if theposition['instrument'] == instrument:
            breakevenprice = theposition["long"]["averagePrice"]

    breakevenprice = float(breakevenprice)

    global program_running
    program_running = True


    if position == "long":

        while program_running:

            running.configure(text="Long position loop running.", text_color="green")

            # check price of candles 
            candle = oanda.getCandles(timeframe, 1 ,instrument)
            recentcandleprice = candle['candles'][0]['mid']['o']
            print(recentcandleprice)

            # if recent candle price > partial close price
            if float(recentcandleprice) > partialcloseprice:

                print("Price has crossed the alert.")


                #close partially
                if partialclose_.get() == 1:
                    oanda.partialClosePosition(instrument, partialcloseunits)

                if movestoploss_.get() == 1:
                    oanda.replaceOrder(tradeid, breakevenprice)
                
                program_running = False

            # wait 1 minute to run command again 
            time.sleep(15)
            root.after(15)
    elif position == "short":

        while program_running:
            running.configure(text="Short position loop running.", text_color="green")

            # check price of candles 
            candle = oanda.getCandles(timeframe, 1 ,instrument)
            recentcandleprice = candle['candles'][0]['mid']['o']

            # if recent candle price < partial close price
            if recentcandleprice < partialcloseprice:

                print("Price has crossed the alert.")

                if partialclose_.get() == 1:
                    oanda.partialClosePosition(instrument, -partialcloseunits)

                if movestoploss_.get() == 1:
                    oanda.replaceOrder(tradeid, breakevenprice)
                
                program_running = False

            # wait 1 minute to run command again
            time.sleep(15) 
            root.after(15)

    
def runProgram1():

    print("access token" + access_Token.get())

    print("account id" + accountId.get())    

    partialcloseprice = partialcloseprice_.get()

    partialcloseunits = partialcloseunits_.get()

    position = position_.get()
    position = position.lower()
    print(position)

    instrument = instrument_.get()

    timeframe = timeframe_.get()

    global program_running
    program_running = True

    print("Partial close price: " + partialcloseprice )
    print("Partial close units" + partialcloseunits + " \n instrument" + instrument + "\n timeframe" + timeframe)

    if position == "long":
        running.configure(text="Long position loop running.", text_color="green")
        while program_running:

            
            if partialclose_.get() == 1:
                print("Partial close working")
            if movestoploss_.get() == 1:
                print("move stop loss working")
                

            # wait 1 minute to run command again  
            root.after(15, time.sleep(15))
            
            
    elif position == "short":
        running.configure(text="Long position loop running.", text_color="green")

        while program_running:    

            
            if partialclose_.get() == 1:
                print("Partial close working")
            if movestoploss_.get() == 1:
                print("move stop loss working")
                
            

            # wait 1 minute to run command again 
            time.sleep(15)
            root.after(15)

    print("Aborted")
    running.configure(text="Stopped running", text_color="red")


frame = customtkinter.CTkFrame(master=root)

frame.pack(pady=20, padx=60, fill="both", expand=True)

title = customtkinter.CTkLabel(master=frame, text="Oanda Forex Risk Manager")
title.pack(pady=24,padx=20)


title = customtkinter.CTkLabel(master=frame, text="Note: feel free to check the source code if you are unsure of putting in your access token")
title.pack(pady=12,padx=10)

access_Token = customtkinter.CTkEntry(master=frame, placeholder_text="Access Token: ", width=300)
access_Token.pack(pady=12, padx=10)

accountId = customtkinter.CTkEntry(master=frame, placeholder_text="Account ID: ", width=300)
accountId.pack(pady=12, padx=10)

partialcloseunits_ = customtkinter.CTkEntry(master=frame, placeholder_text="Enter how much units you want to close: ", width=300)
partialcloseunits_.pack(pady=12, padx=10)

partialcloseprice_  = customtkinter.CTkEntry(master=frame, placeholder_text="Enter what price level you want to close the trade at: ", width=300)
partialcloseprice_.pack(pady=12, padx=10)

position_ = customtkinter.CTkEntry(master=frame, placeholder_text="Long or short trade? ", width=300)
position_.pack(pady=12, padx=10)

instrument_ = customtkinter.CTkEntry(master=frame, placeholder_text="Which forex pair? EX: EUR_USD", width=300)
instrument_.pack(pady=12, padx=10)

timeframe_ = customtkinter.CTkEntry(master=frame, placeholder_text="Which timeframe? EX: H4 S5 M15 ", width=300)
timeframe_.pack(pady=12, padx=10)

movestoploss_ = customtkinter.CTkCheckBox(master=frame, text="Move Stop loss?")
movestoploss_.pack(pady=12, padx=10)


partialclose_ = customtkinter.CTkCheckBox(master=frame, text="Partial close?")
partialclose_.pack(pady=12, padx=10)

submit = customtkinter.CTkButton(master=frame, text="Enter", command = runProgram1)
submit.pack(pady=12, padx=10)

abort = customtkinter.CTkButton(master=frame, text="Abort", fg_color="red", hover_color="red")
abort.pack(pady=12, padx=10)


running = customtkinter.CTkLabel(master=frame, text="Not running", text_color="red")

running.pack(pady=12,padx=10)




root.mainloop()