import React, { useState, useEffect } from 'react';  // Import React and necessary hooks
import axios from 'axios';  // Import axios for making HTTP requests

function PriceCalculator() {
  // Define state variables for BTC quantity and price in USDC
  const [btcQuantity, setBtcQuantity] = useState(0);
  const [priceUsdc, setPriceUsdc] = useState(0);

  // useEffect hook to fetch price data when btcQuantity changes
  useEffect(() => {
    // Define async function to fetch price data
    const fetchPrice = async () => {
      try {
        // Send GET request to API endpoint to fetch price data based on btcQuantity
        const response = await axios.get(`${window.API_BASE_URL}/price/?btc_quantity=${btcQuantity}`);
        // Update priceUsdc state with the fetched price data
        setPriceUsdc(response.data.price_usdc);
      } catch (error) {
        // Handle errors if any occur during fetching
        console.error('Error fetching price:', error);
      }
    };

    // Call fetchPrice function when btcQuantity changes
    fetchPrice();
  }, [btcQuantity]);  // Dependency array to trigger useEffect when btcQuantity changes

  // Event handler function to update btcQuantity state when input value changes
  const handleInputChange = (event) => {
    setBtcQuantity(event.target.value);  // Update btcQuantity state with new input value
  };

  // Render the PriceCalculator component
  return (
    <div className="PriceCalculator">  {/* Container div with PriceCalculator class */}
      <h1>Orderbook Price</h1>  {/* Heading */}
      <div>  {/* Div for input and price display */}
        <input
          type="number"
          value={btcQuantity}  // Bind input value to btcQuantity state
          onChange={handleInputChange}  // Call handleInputChange on input change
          placeholder="Enter quantity of BTC"  // Placeholder text for input field
        />
        <p>Price in USDC: {priceUsdc}</p>  {/* Display price in USDC */}
      </div>
    </div>
  );
}

export default PriceCalculator;  // Export PriceCalculator component as default
