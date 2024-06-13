from oandaclass import Oanda
import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

oanda = Oanda(os.getenv("ACCESS_TOKEN"))

oanda.setCurrentAccount('101-001-24797201-002')

# ALL POSITIONS WILL BE RISK MANAGED

# GOAL: take all current positions and risk manage them according to your rules
def execute_manager():
    # Get all positions
    positions = oanda.getAllPositions()

    # lets first read whats in positions
    positions = positions['positions']
    print(json.dumps(positions, indent=4))

    # read whats in orders
    # orders = oanda.getAllOrders()
    # print(json.dumps(orders, indent=4))

    # move each to break even with a loop
    for position in positions:
        print(json.dumps(position, indent=4))
        # what do you need for breakeven stop loss move

        # Determine if the position is long or short
        is_long = position['long']['units'] != "0"

        # Extract the first trade ID based on the position
        #averagePrice + commission for BE
        if is_long:
            first_trade_id = position['long']['tradeIDs'][0]

            average_price = position['long']['averagePrice']
        else:
            first_trade_id = position['short']['tradeIDs'][0]

            average_price = position['short']['averagePrice']

        # get pair
        instrument = position['instrument']

        # use getallorders to get the ID of the stop loss, filter by currency pair
        orders = oanda.getAllOrders(currency_pair=instrument, allpairs=False)
        print(json.dumps(orders, indent=4))

        # price to breakeven at , take profit percentage


        # call breakeven
        move_breakeven()

        # set eachs partials 
        set_partials()
        

# function calculate breakeven
def move_breakeven():
    pass

# function for partials (what percentage )
def set_partials():
    pass


execute_manager()



