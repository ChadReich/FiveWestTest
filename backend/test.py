import asyncio
import json
import websockets
from typing import Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from collections import defaultdict
import hashlib
from datetime import datetime

# Create FastAPI instance
app = FastAPI()

# Define a Pydantic model for the order book update
class OrderBookUpdate(BaseModel):
    type: str
    currencyPairSymbol: str
    data: dict

# Function to generate request signature
def sign_request(api_key_secret, timestamp, verb, path, body=""):
    message = f"{timestamp}{verb.upper()}{path}{body}"
    signature = hashlib.sha512(message.encode()).hexdigest()
    return signature

# Function to get authentication headers
def get_auth_headers(api_key, api_key_secret, path):
    timestamp = int(datetime.now().timestamp() * 1000)
    signature = sign_request(api_key_secret, timestamp, "GET", path)
    headers = {
        "X-VALR-API-KEY": api_key,
        "X-VALR-SIGNATURE": signature,
        "X-VALR-TIMESTAMP": str(timestamp)
    }
    return headers

# Coroutine to connect to the VALR trade WebSocket and subscribe to updates
async def connect_to_valr_trade_websocket(api_key, api_key_secret):
    uri = "wss://api.valr.com/ws/trade"
    headers = get_auth_headers(api_key, api_key_secret, "/ws/trade")
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # Send subscription message for FULL_ORDERBOOK_UPDATE events
        message = {
            "type": "SUBSCRIBE",
            "subscriptions": [
                {
                    "event": "FULL_ORDERBOOK_UPDATE",
                    "pairs": [
                        "SOLZAR",
                        "BTCUSDC"
                        ]
                    }
                ]
            }
        await websocket.send(json.dumps(message))

        # Function to send a PING message every 30 seconds
        async def send_ping():
            while True:
                print("Sending PING event to VALR")
                await asyncio.sleep(30)
                await websocket.send(json.dumps({"type": "PING"}))

        # Start the task to send PING messages
        asyncio.create_task(send_ping())

        # Continuously receive and process updates from the WebSocket
        while True:
            try:
                data = await websocket.recv()
                print(data)
                update_data = json.loads(data)
                if update_data["type"] == "FULL_ORDERBOOK_SNAPSHOT":
                    order_book.process_full_orderbook_snapshot(update_data)
                elif update_data["type"] == "FULL_ORDERBOOK_UPDATE":
                    order_book.process_full_orderbook_update(update_data)
                elif update_data["type"] == "PONG":
                    print("Received PONG event from VALR")  # Handle PONG event
            except Exception as e:
                print(f"Error: {e}")

# Define a class to handle order book operations
class OrderBook:
    def __init__(self):
        self.order_book = defaultdict(lambda: defaultdict(list))

    # Process a full order book snapshot update
    def process_full_orderbook_snapshot(self, update_data):
        currency_pair = update_data["currencyPairSymbol"]
        self.order_book[currency_pair] = {
            "Asks": {},
            "Bids": {}
        }
        for side in ["Asks", "Bids"]:
            for order in update_data["data"][side]:
                self.order_book[currency_pair][side][order["Price"]] = {
                    "orderId": order["Orders"][0]["orderId"],
                    "quantity": order["Orders"][0]["quantity"]
                }

    # Process a full order book update
    def process_full_orderbook_update(self, update_data):
        currency_pair = update_data["currencyPairSymbol"]
        for side in ["Asks", "Bids"]:
            for order in update_data["data"][side]:
                price = order["Price"]
                if order["Orders"][0]["quantity"] == "0":
                    # Remove order if quantity is 0
                    if price in self.order_book[currency_pair][side]:
                        del self.order_book[currency_pair][side][price]
                else:
                    # Update or add order
                    self.order_book[currency_pair][side][price] = {
                        "orderId": order["Orders"][0]["orderId"],
                        "quantity": order["Orders"][0]["quantity"]
                    }

    # Get the order book for a specific currency pair
    def get_order_book(self, currency_pair):
        return self.order_book.get(currency_pair)

# Create an instance of the OrderBook class
order_book = OrderBook()

# API endpoints
# Define a route to get the order book for a specific currency pair
@app.get("/orderbook/{currency_pair}")
async def get_order_book(currency_pair: str):
    return order_book.get_order_book(currency_pair)

# Define a route to calculate the price of a specific quantity of a given currency
@app.get("/price/")
async def calculate_price(
    currency_pair: str = Query(..., description="Currency pair (e.g. BTCZAR)"),
    quantity: float = Query(..., description="Quantity of the chosen coin"),
):
    if currency_pair not in order_book.order_book:
        return {"error": "Order book data not available for the specified currency pair."}

    asks = order_book.order_book[currency_pair]["Asks"]
    target_currency_price = 0.0
    remaining_quantity = quantity

    for ask in asks:
        for order in asks[ask]:
            order_quantity = float(order["quantity"])
            order_price = float(ask)

            if remaining_quantity >= order_quantity:
                target_currency_price += order_quantity * order_price
                remaining_quantity -= order_quantity
            else:
                target_currency_price += remaining_quantity * order_price
                remaining_quantity = 0
                break

        if remaining_quantity == 0:
            break

    return {"price": target_currency_price}

# Run the WebSocket connection coroutine when the application starts/script is executed
if __name__ == "__main__":
    api_key = "da359e4d7228862915cc997d2bbffc54607562c2dfb724da693d36c8a3d50eca"
    api_key_secret = "848c86f33ad1ba6591340688ce7bfc29f434e3e587ad61329b012e8ebb12c212"
    asyncio.run(connect_to_valr_trade_websocket(api_key, api_key_secret))
    import uvicorn
