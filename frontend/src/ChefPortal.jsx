import { useState, useEffect } from 'react';
import { STAFF_API } from './config/staff';

function ChefPortal({ token }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
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
      setOrders(data.filter(o => o.status === 'confirmed' || o.status === 'COOKING'));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const startCooking = async (orderId) => {
    await updateOrderStatus(orderId, 'COOKING');
  };

  const markAsReady = async (orderId) => {
    await updateOrderStatus(orderId, 'READY');
  };

  const updateOrderStatus = async (orderId, status) => {
    try {
      await fetch(`${STAFF_API}/order/${orderId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status })
      });
      
      loadOrders();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div>Loading orders...</div>;

  return (
    <div className="portal-container chef-theme">
      <h2>👨‍🍳 Chef Portal - Pending Orders</h2>
      {orders.length === 0 ? (
        <p>No pending orders</p>
      ) : (
        <div className="order-grid">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <h3>Order #{order.id}</h3>
              <p className={`status-badge status-${order.status}`}>
                Status: {order.status}
              </p>
              <div className="order-items">
                {order.items}
              </div>
              {order.status === 'confirmed' && (
                <button 
                  className="btn-primary"
                  onClick={() => startCooking(order.id)}
                >
                  Start Cooking
                </button>
              )}
              {order.status === 'COOKING' && (
                <button 
                  className="btn-success"
                  onClick={() => markAsReady(order.id)}
                >
                  Mark as Ready
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ChefPortal;