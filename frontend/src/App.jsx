import { useState, useEffect } from 'react';
import Menu from './Menu';
import './App.css';

import { STAFF_API } from './config/staff';

function ChefView() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetch(`${STAFF_API}/orders/pending`)
      .then(res => res.json())
      .then(data => setOrders(data))
      .catch(err => console.error(err));
  }, []);

  const updateStatus = async (orderId, status) => {
    await fetch(`${STAFF_API}/order/${orderId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    setOrders(orders.filter(o => {
      if (o.id === orderId) return status !== 'READY';
      return true;
    }));
  };

  return (
    <div className="staff-view">
      <h2>👨‍🍳 Chef Dashboard - Pending Orders</h2>
      {orders.length === 0 ? <p>No pending orders</p> : (
        <div className="order-cards">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <h3>Order #{order.id}</h3>
              <p className="status">Status: {order.status}</p>
              <p className="items">{order.items}</p>
              <div className="actions">
                {order.status === 'confirmed' && (
                  <button onClick={() => updateStatus(order.id, 'COOKING')}>Start Cooking</button>
                )}
                {order.status === 'COOKING' && (
                  <button onClick={() => updateStatus(order.id, 'READY')}>Mark as Ready</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function WaiterView() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetch(`${STAFF_API}/orders/pending`)
      .then(res => res.json())
      .then(data => setOrders(data.filter(o => o.status === 'READY')))
      .catch(err => console.error(err));
  }, []);

  const markServed = async (orderId) => {
    await fetch(`${STAFF_API}/order/${orderId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'SERVED' })
    });
    setOrders(orders.filter(o => o.id !== orderId));
  };

  return (
    <div className="staff-view">
      <h2>🍽️ Waiter Dashboard - Ready Orders</h2>
      {orders.length === 0 ? <p>No ready orders</p> : (
        <div className="order-cards">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <h3>Order #{order.id}</h3>
              <p className="items">{order.items}</p>
              <button onClick={() => markServed(order.id)}>Mark as Served</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CashierView() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetch(`${STAFF_API}/orders/pending`)
      .then(res => res.json())
      .then(data => setOrders(data.filter(o => o.status === 'SERVED')))
      .catch(err => console.error(err));
  }, []);

  const completePayment = async (orderId) => {
    await fetch(`${STAFF_API}/order/${orderId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'PAID' })
    });
    setOrders(orders.filter(o => o.id !== orderId));
  };

  return (
    <div className="staff-view">
      <h2>💰 Cashier Dashboard - Awaiting Payment</h2>
      {orders.length === 0 ? <p>No orders awaiting payment</p> : (
        <div className="order-cards">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <h3>Order #{order.id}</h3>
              <p className="total">Total: ${order.total_amount?.toFixed(2) || '0.00'}</p>
              <button onClick={() => completePayment(order.id)}>Complete Payment</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function BossView() {
  const [stats, setStats] = useState({ total_revenue: 0, total_orders: 0 });

  useEffect(() => {
    fetch(`${STAFF_API}/analytics/revenue`)
      .then(res => res.json())
      .then(data => setStats(data.summary))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="staff-view">
      <h2>📊 Boss Dashboard</h2>
      <div className="stats-cards">
        <div className="stat-card">
          <h3>Total Revenue</h3>
          <p className="stat-value">${stats.total_revenue?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Total Orders</h3>
          <p className="stat-value">{stats.total_orders || 0}</p>
        </div>
      </div>
    </div>
  );
}

function ManagerView() {
  const [dishes, setDishes] = useState([]);
  const [newDish, setNewDish] = useState({ name: '', description: '', price: '' });

  useEffect(() => {
    fetch(`${STAFF_API}/dishes`)
      .then(res => res.json())
      .then(data => setDishes(data))
      .catch(err => console.error(err));
  }, []);

  const addDish = async (e) => {
    e.preventDefault();
    const res = await fetch(`${STAFF_API}/dishes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newDish)
    });
    const dish = await res.json();
    setDishes([...dishes, dish]);
    setNewDish({ name: '', description: '', price: '' });
  };

  const deleteDish = async (id) => {
    await fetch(`${STAFF_API}/dishes/${id}`, { method: 'DELETE' });
    setDishes(dishes.filter(d => d.id !== id));
  };

  return (
    <div className="staff-view">
      <h2>🛠️ Manager Dashboard - Menu Management</h2>
      <form onSubmit={addDish} className="add-dish-form">
        <input
          placeholder="Dish Name"
          value={newDish.name}
          onChange={e => setNewDish({...newDish, name: e.target.value})}
          required
        />
        <input
          placeholder="Description"
          value={newDish.description}
          onChange={e => setNewDish({...newDish, description: e.target.value})}
          required
        />
        <input
          type="number"
          placeholder="Price"
          value={newDish.price}
          onChange={e => setNewDish({...newDish, price: e.target.value})}
          step="0.01"
          required
        />
        <button type="submit">Add New Dish</button>
      </form>
      <table className="dishes-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Price</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {dishes.map(dish => (
            <tr key={dish.id}>
              <td>{dish.id}</td>
              <td>{dish.name}</td>
              <td>{dish.description}</td>
              <td>${dish.price?.toFixed(2)}</td>
              <td><button className="delete-btn" onClick={() => deleteDish(dish.id)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  const [role, setRole] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setRole(params.get('role'));
  }, []);

  const renderStaffView = () => {
    switch (role) {
      case 'CHEF': return <ChefView />;
      case 'WAITER': return <WaiterView />;
      case 'CASHIER': return <CashierView />;
      case 'BOSS': return <BossView />;
      case 'MANAGER': return <ManagerView />;
      default: return <Menu />;
    }
  };

  return (
    <div className="app">
      {renderStaffView()}
    </div>
  );
}

export default App;