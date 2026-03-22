import { useState, useEffect } from 'react';
import ChefPortal from './ChefPortal';
import WaiterPortal from './WaiterPortal';
import CashierPortal from './CashierPortal';

function StaffDashboard() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const role = localStorage.getItem('user_role');
    
    if (token && role) {
      setUser({ token, role });
    }
  }, []);

  if (!user) {
    return <div>Loading...</div>;
  }

  switch (user.role) {
    case 'CHEF':
      return <ChefPortal token={user.token} />;
    case 'WAITER':
      return <WaiterPortal token={user.token} />;
    case 'CASHIER':
      return <CashierPortal token={user.token} />;
    default:
      return <div>Invalid role: {user.role}</div>;
  }
}

export default StaffDashboard;