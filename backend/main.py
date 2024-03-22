import asyncio
import json
import websockets
from typing import List
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.orderbook import OrderBook

# Create FastAPI instance
app = FastAPI()

# Define a Pydantic model for the order book update
class OrderBookUpdate(BaseModel):
    type: str
    currencyPairSymbol: str
    data: dict

# Create an instance of the OrderBook class
order_book = OrderBook()
#print("Order book content:", order_book.order_book)

# Coroutine to connect to the VALR trade WebSocket and subscribe to updates
async def connect_to_valr_trade_websocket():
    uri = "wss://api.valr.com/ws/trade"
    async with websockets.connect(uri) as websocket:
        # Send subscription message for BTCUSDC FULL_ORDERBOOK_UPDATE events
        message = {
            "type": "SUBSCRIBE",
            "subscriptions": [
                {
                    "event": "FULL_ORDERBOOK_UPDATE",
                    "pairs": ["SOLZAR",
                              "BTCUSDC"]
                }
            ]
        }
        await websocket.send(json.dumps(message))

        # Continuously receive and process updates from the WebSocket
        while True:
            try:
                data = await websocket.recv()
                print("Received data from WebSocket:", data)
                update_data = json.loads(data)
                if update_data["type"] == "FULL_ORDERBOOK_SNAPSHOT":
                    print("Processing full order book snapshot update:", update_data)
                    order_book.process_full_orderbook_snapshot(update_data)
                elif update_data["type"] == "FULL_ORDERBOOK_UPDATE":
                    order_book.process_full_orderbook_update(update_data)
                    print("Processing full order book update:", update_data)

            except Exception as e:
                print(f"Error: {e}")


# API endpoints
# Define a route to retrieve the current state of the order book
@app.get("/orderbook")
async def get_order_book():
    # Retrieve the order book data
    order_book_data = order_book.get_order_book_data()

    # Check if the order book is empty
    if not order_book_data:
        raise HTTPException(status_code=404, detail="Order book not found")

    # Return the order book data
    return order_book_data

# Define a route to calculate the price of a specific quantity of BTC in USDC
@app.get("/price/")
async def calculate_price(
    btc_quantity: float = Query(..., description="Quantity of BTC")
    print("Calculating price for BTC quantity:", btc_quantity)
):
    currency_pair = "BTCUSDC"
    if currency_pair not in order_book.order_book:
        return {"error": "Order book data not available for BTCUSDC pair."}

    asks = order_book.order_book[currency_pair]["Asks"]
    print("Asks in order book:", asks)
    target_currency_price = 0.0
    remaining_quantity = btc_quantity

    for ask_price, orders in asks.items():
        for order_quantity in orders.items():
            order_quantity = float(order_quantity)
            ask_price = float(ask_price)
            print("Processing order:", "Quantity:", order_quantity, "Ask Price:", ask_price)

            if remaining_quantity >= order_quantity:
                target_currency_price += order_quantity * ask_price
                remaining_quantity -= order_quantity
            else:
                target_currency_price += remaining_quantity * ask_price
                remaining_quantity = 0
                break

        if remaining_quantity == 0:
            break

    print("Final price in USDC:", target_currency_price)
    return {"price_usdc": target_currency_price}

# Route to serve the React JS frontend
@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("../frontend/public/index.html")


# Run the WebSocket connection coroutine when the application starts/script is executed
if __name__ == "__main__":
    asyncio.run(connect_to_valr_trade_websocket())
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
