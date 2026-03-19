import { useState, useEffect } from 'react';
import { API_BASE } from './config';

const Menu = () => {
  const [dishes, setDishes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDishes();
  }, []);

  const fetchDishes = async () => {
    try {
      const response = await fetch(`${API_BASE}/dishes`);
      if (!response.ok) {
        throw new Error('Failed to fetch dishes');
      }
      const data = await response.json();
      setDishes(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const placeOrder = async () => {
    try {
      const response = await fetch(`${API_BASE}/order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: dishes.map(dish => ({ id: dish.id, quantity: 1 })),
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to place order');
      }
      
      const result = await response.json();
      alert(`Order placed successfully! Order ID: ${result.orderId}`);
    } catch (err) {
      alert(`Error placing order: ${err.message}`);
    }
  };

  if (loading) return <div>Loading menu...</div>;
  if (error) return <div>Error loading menu: {error}</div>;

  return (
    <div className="menu-container">
      <h1>Restaurant Menu</h1>
      <div className="dishes-grid">
        {dishes.map(dish => (
          <div key={dish.id} className="dish-card">
            <h3>{dish.name}</h3>
            <p>{dish.description}</p>
            <p className="price">${dish.price}</p>
          </div>
        ))}
      </div>
      <button onClick={placeOrder} className="order-button">
        Place Order
      </button>
    </div>
  );
};

export default Menu;
