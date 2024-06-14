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
    #print(json.dumps(positions, indent=4))

    if not positions:
        print("You have no active positions")
        return

    # read whats in orders
    # orders = oanda.getAllOrders()
    # print(json.dumps(orders, indent=4))

    # move each to break even with a loop
    for position in positions:
        #print(json.dumps(position, indent=4))
        # what do you need for breakeven stop loss move

        # Determine if the position is long or short
        is_long = position['long']['units'] != "0"

        # Extract the first trade ID based on the position
        #averagePrice + commission for BE
        if is_long:
            first_trade_id = position['long']['tradeIDs'][0]

            average_price = float(position['long']['averagePrice'])
        else:
            first_trade_id = position['short']['tradeIDs'][0]

            average_price = float(position['short']['averagePrice'])

        # get pair
        instrument = position['instrument']

        # use getallorders to get the ID of the stop loss, filter by currency pair
        order = oanda.getAllOrders(currency_pair=instrument, allpairs=False)
        #print(json.dumps(order, indent=4))

        
        take_profit_price = float([order1 for order1 in order['orders'] if order1['type'] == 'TAKE_PROFIT'][0]['price'])

        # Calculate the difference, overall pips earned
        difference = take_profit_price - average_price


        percentage = 0.15
        timeframe = "M1"

        tricksystem = True

        # call breakeven
        while tricksystem:
            print("-------------------------")
            move_breakeven( first_trade_id, order, difference, is_long, percentage, average_price, timeframe, instrument)
            time.sleep(60)

        # set eachs partials 
        set_partials()
        


# Function to calculate breakeven
def move_breakeven( trade_id, order, difference, is_long, percentage, average_price, timeframe, instrument):
    stop_loss_order = next((o for o in order['orders'] if o['type'] == 'STOP_LOSS'), None)
    
    if not stop_loss_order:
        print(f"No STOP_LOSS order found for trade ID {trade_id}")
        return
    
    # Calculate new stop loss price
    print("Average Price:", average_price)
    new_stop_loss_price = average_price + (difference * percentage)

    # Check if current price is above the average price
    candle = oanda.getCandles(timeframe, 1 ,instrument)
    recentcandleprice = candle['candles'][0]['mid']['o']
    print("Candle price:", recentcandleprice)
    current_price = float(recentcandleprice)
    print("Target stop loss price:", new_stop_loss_price)
    print("Is long:", is_long)

    # Check if the new stop loss price is favorable
    if (is_long and new_stop_loss_price > current_price) or (not is_long and new_stop_loss_price < current_price):
        print(f"Target stop-loss price {new_stop_loss_price} is not favorable for breakeven move as the current price {current_price} is not above/under it for trade ID {trade_id} This trade is {"Long" if is_long else "Short"}")
        return

    
    stop_loss_id = stop_loss_order['id']
    average_price = str(average_price)
    print(average_price)
    

    
    # Replace the order wiqth a average price at breakeven
    response = oanda.replaceOrder(trade_id, average_price, type="STOP_LOSS", timeInForce=stop_loss_order['timeInForce'], orderspecify=stop_loss_id)
    print(f"Breakeven move response for trade ID {trade_id}: {json.dumps(response, indent=4)}")

# function for partials (what percentage )
def set_partials():
    pass


execute_manager()



