from collections import defaultdict

class OrderBook:
    def __init__(self):
        # Initialize an empty order book
        self.order_book = defaultdict(dict)

        # Print a message to indicate that the order book is initialized
        #print("Order book initialized successfully.")

        # Print the content of the order book
        print("Order book content:", self.order_book)

    def process_full_orderbook_snapshot(self, update_data):
        currency_pair = update_data["currencyPairSymbol"]
        self.order_book[currency_pair] = defaultdict(dict, {"Asks": {}, "Bids": {}})
        #print("Processing full order book snapshot update:", update_data)  # Print the update data

        for side in ["Asks", "Bids"]:
            for order_data in update_data["data"][side]:
                price = order_data["Price"]
                order_id = order_data["Orders"][0]["orderId"]
                quantity = order_data["Orders"][0]["quantity"]
                self.order_book[currency_pair][side][price] = {order_id: quantity}

        # Print the updated order book content
        #print("Updated order book content:", self.order_book)

    def process_full_orderbook_update(self, update_data):
        currency_pair = update_data["currencyPairSymbol"]
        order_book_data = {"Asks": {}, "Bids": {}}

        for side in ["Asks", "Bids"]:
            for order_data in update_data["data"][side]:
                price = float(order_data["Price"])  # Convert price to float
                order_id = order_data["Orders"][0]["orderId"]
                quantity = float(order_data["Orders"][0]["quantity"])  # Convert quantity to float

                if quantity == 0:
                    # Remove order if quantity is 0
                    if price in order_book_data[side]:
                        if order_id in order_book_data[side][price]:
                            del order_book_data[side][price][order_id]
                            # Remove the price level if it becomes empty
                            if not order_book_data[side][price]:
                                del order_book_data[side][price]
                else:
                    # Update or add order
                    if price in order_book_data[side]:
                        order_book_data[side][price][order_id] = quantity
                    else:
                        order_book_data[side][price] = {order_id: quantity}

        # Update self.order_book with the new data structure
        self.order_book[currency_pair] = order_book_data

        # Print the updated order book content
        #print("Updated order book content:", self.order_book)

    def get_order_book_data(self):
        """
        Returns the order book data.

        Returns:
        dict: The order book data.
        """
        return self.order_book
