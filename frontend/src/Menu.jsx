import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { CUSTOMER_API } from './config/customer';

const Menu = () => {
  const [dishes, setDishes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDishes, setSelectedDishes] = useState(new Set());

  useEffect(() => {
    fetchDishes();
  }, []);

  const toggleDish = (dishId) => {
    setSelectedDishes((prev) => {
      const next = new Set(prev);
      if (next.has(dishId)) {
        next.delete(dishId);
      } else {
        next.add(dishId);
      }
      return next;
    });
  };

  const fetchDishes = async () => {
    try {
      const response = await fetch(`${CUSTOMER_API}/dishes`);
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
    if (selectedDishes.size === 0) {
      alert('Please select at least one dish before placing an order.');
      return;
    }

    try {
      const items = Array.from(selectedDishes).map((id) => ({ id, quantity: 1 }));
      const response = await fetch(`${CUSTOMER_API}/order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ items }),
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
      <div style={{ textAlign: 'right', marginBottom: '1rem' }}>
        <Link to="/staff" className="order-button" style={{ fontSize: '0.8rem' }}>Staff Portal</Link>
      </div>
      <h1>Restaurant Menu</h1>
      <div className="dishes-grid">
        {dishes.map(dish => (
          <div
            key={dish.id}
            className={`dish-card ${selectedDishes.has(dish.id) ? 'selected' : ''}`}
            onClick={() => toggleDish(dish.id)}
          >
            <h3>{dish.name}</h3>
            <p>{dish.description}</p>
            <p className="price">${dish.price}</p>
          </div>
        ))}
      </div>
      <button onClick={placeOrder} className="order-button">
        Place Order{selectedDishes.size > 0 ? ` (${selectedDishes.size} selected)` : ''}
      </button>
    </div>
  );
};

export default Menu;
