import { useState, useEffect } from 'react';
import { STAFF_API } from './config/staff';

function CashierPortal({ token }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAwaitingPaymentOrders();
  }, []);

  const loadAwaitingPaymentOrders = async () => {
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
      setOrders(data.filter(o => o.status === 'SERVED'));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const completePayment = async (orderId) => {
    try {
      await fetch(`${STAFF_API}/order/${orderId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: 'PAID' })
      });
      
      setOrders(orders.filter(o => o.id !== orderId));
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div>Loading orders...</div>;

  return (
    <div className="portal-container cashier-theme">
      <h2>💰 Cashier Portal - Awaiting Payment</h2>
      {orders.length === 0 ? (
        <p>No orders awaiting payment</p>
      ) : (
        <div className="order-grid">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <h3>Order #{order.id}</h3>
              <div className="order-items">
                {order.items}
              </div>
              <p className="total-amount">
                Total: ${order.total_amount?.toFixed(2) || '0.00'}
              </p>
              <button 
                className="btn-success"
                onClick={() => completePayment(order.id)}
              >
                Complete Payment
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CashierPortal;