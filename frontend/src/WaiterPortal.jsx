import { useState, useEffect } from 'react';
import { STAFF_API } from './config/staff';

function WaiterPortal({ token }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReadyOrders();
  }, []);

  const loadReadyOrders = async () => {
    try {
      const response = await fetch(`${STAFF_API}/orders/pending`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch orders');
      }
      
      const data = await response.json();
      setOrders(data.filter(o => o.status === 'READY'));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const markAsServed = async (orderId) => {
    try {
      await fetch(`${STAFF_API}/order/${orderId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: 'SERVED' })
      });
      
      setOrders(orders.filter(o => o.id !== orderId));
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div>Loading orders...</div>;

  return (
    <div className="portal-container waiter-theme">
      <h2>🍽️ Waiter Portal - Ready Orders</h2>
      {orders.length === 0 ? (
        <p>No ready orders</p>
      ) : (
        <div className="order-grid">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <h3>Order #{order.id}</h3>
              <div className="order-items">
                {order.items}
              </div>
              <button 
                className="btn-secondary"
                onClick={() => markAsServed(order.id)}
              >
                Mark as Served
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default WaiterPortal;