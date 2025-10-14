# Service Layer Usage Examples

This file contains practical examples of using the service layer in your React components.

## Setup

```typescript
// Import services you need
import {
  authService,
  mealsService,
  depositsService,
  expensesService,
  usersService,
  notificationsService,
  menuService,
  settingsService,
  announcementsService
} from './services';
```

## Authentication Flow

### Login Component

```typescript
import { useState } from 'react';
import { authService } from './services';
import toast from 'react-hot-toast';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const result = await authService.login({ email, password });

    if (result.success) {
      toast.success('Login successful!');
      // Redirect to dashboard
    } else {
      toast.error(result.error);
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Loading...' : 'Login'}
      </button>
    </form>
  );
}
```

### Auth Context Provider

```typescript
import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from './services';
import { User } from './types/database.types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check current session
    const checkAuth = async () => {
      const result = await authService.getCurrentUser();
      if (result.success) {
        setUser(result.data);
      }
      setLoading(false);
    };

    checkAuth();

    // Listen to auth changes
    const { data: { subscription } } = authService.onAuthStateChange(
      async (authUser) => {
        if (authUser) {
          const userResult = await authService.getCurrentUser();
          if (userResult.success) {
            setUser(userResult.data);
          }
        } else {
          setUser(null);
        }
      }
    );

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  const logout = async () => {
    const result = await authService.logout();
    if (result.success) {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

## Meal Management

### Mark Meals Component

```typescript
import { useState, useEffect } from 'react';
import { mealsService } from './services';
import { useAuth } from './contexts/AuthContext';
import toast from 'react-hot-toast';

function MealSelector({ date }: { date: string }) {
  const { user } = useAuth();
  const [meal, setMeal] = useState({
    breakfast: false,
    lunch: false,
    dinner: false,
    guest_breakfast: 0,
    guest_lunch: 0,
    guest_dinner: 0
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchMeal = async () => {
      if (!user) return;

      const result = await mealsService.getMealByUserAndDate(user.id, date);
      if (result.success && result.data) {
        setMeal({
          breakfast: result.data.breakfast,
          lunch: result.data.lunch,
          dinner: result.data.dinner,
          guest_breakfast: result.data.guest_breakfast,
          guest_lunch: result.data.guest_lunch,
          guest_dinner: result.data.guest_dinner
        });
      }
    };

    fetchMeal();
  }, [user, date]);

  const handleSave = async () => {
    if (!user) return;

    setLoading(true);
    const result = await mealsService.upsertMeal({
      user_id: user.id,
      meal_date: date,
      ...meal,
      breakfast_locked: false,
      lunch_locked: false,
      dinner_locked: false
    });

    if (result.success) {
      toast.success('Meals updated successfully!');
    } else {
      toast.error(result.error);
    }

    setLoading(false);
  };

  return (
    <div>
      <h3>Select Meals for {date}</h3>

      <label>
        <input
          type="checkbox"
          checked={meal.breakfast}
          onChange={(e) => setMeal({ ...meal, breakfast: e.target.checked })}
        />
        Breakfast
      </label>

      <label>
        <input
          type="checkbox"
          checked={meal.lunch}
          onChange={(e) => setMeal({ ...meal, lunch: e.target.checked })}
        />
        Lunch
      </label>

      <label>
        <input
          type="checkbox"
          checked={meal.dinner}
          onChange={(e) => setMeal({ ...meal, dinner: e.target.checked })}
        />
        Dinner
      </label>

      <button onClick={handleSave} disabled={loading}>
        {loading ? 'Saving...' : 'Save Meals'}
      </button>
    </div>
  );
}
```

## Deposits Management

### Add Deposit Component

```typescript
import { useState } from 'react';
import { depositsService } from './services';
import { useAuth } from './contexts/AuthContext';
import toast from 'react-hot-toast';

function AddDeposit() {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    amount: 0,
    deposit_date: new Date().toISOString().split('T')[0],
    payment_method: 'cash' as const,
    notes: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setLoading(true);
    const month = formData.deposit_date.slice(0, 7); // YYYY-MM

    const result = await depositsService.createDeposit({
      user_id: user.id,
      amount: formData.amount,
      deposit_date: formData.deposit_date,
      month,
      payment_method: formData.payment_method,
      notes: formData.notes,
      recorded_by: user.id
    });

    if (result.success) {
      toast.success('Deposit added successfully!');
      // Reset form
      setFormData({
        amount: 0,
        deposit_date: new Date().toISOString().split('T')[0],
        payment_method: 'cash',
        notes: ''
      });
    } else {
      toast.error(result.error);
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="number"
        value={formData.amount}
        onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
        placeholder="Amount"
        required
      />

      <input
        type="date"
        value={formData.deposit_date}
        onChange={(e) => setFormData({ ...formData, deposit_date: e.target.value })}
        required
      />

      <select
        value={formData.payment_method}
        onChange={(e) => setFormData({ ...formData, payment_method: e.target.value as any })}
      >
        <option value="cash">Cash</option>
        <option value="upi">UPI</option>
        <option value="online">Online</option>
      </select>

      <textarea
        value={formData.notes}
        onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
        placeholder="Notes (optional)"
      />

      <button type="submit" disabled={loading}>
        {loading ? 'Adding...' : 'Add Deposit'}
      </button>
    </form>
  );
}
```

## Notifications with Real-time Updates

### Notifications Component

```typescript
import { useState, useEffect } from 'react';
import { notificationsService } from './services';
import { useAuth } from './contexts/AuthContext';
import { Notification } from './types/database.types';

function NotificationsList() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!user) return;

    // Fetch initial notifications
    const fetchNotifications = async () => {
      const result = await notificationsService.getNotificationsByUser(user.id);
      if (result.success) {
        setNotifications(result.data || []);
      }

      const countResult = await notificationsService.getUnreadNotificationCount(user.id);
      if (countResult.success) {
        setUnreadCount(countResult.data || 0);
      }
    };

    fetchNotifications();

    // Subscribe to real-time updates
    const unsubscribe = notificationsService.subscribeToNotifications(
      user.id,
      (newNotification) => {
        setNotifications((prev) => [newNotification, ...prev]);
        setUnreadCount((prev) => prev + 1);
      }
    );

    return () => {
      unsubscribe();
    };
  }, [user]);

  const handleMarkAsRead = async (id: string) => {
    const result = await notificationsService.markNotificationAsRead(id);
    if (result.success) {
      setNotifications((prev) =>
        prev.map((notif) =>
          notif.id === id ? { ...notif, is_read: true } : notif
        )
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    }
  };

  return (
    <div>
      <h3>Notifications ({unreadCount} unread)</h3>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          style={{
            backgroundColor: notification.is_read ? '#f5f5f5' : '#fff3cd',
            padding: '10px',
            marginBottom: '10px'
          }}
        >
          <h4>{notification.title}</h4>
          <p>{notification.message}</p>
          {!notification.is_read && (
            <button onClick={() => handleMarkAsRead(notification.id)}>
              Mark as Read
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
```

## Menu Display

### Today's Menu Component

```typescript
import { useState, useEffect } from 'react';
import { menuService } from './services';
import { Menu } from './types/database.types';

function TodayMenu() {
  const [menu, setMenu] = useState<Menu | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMenu = async () => {
      const result = await menuService.getTodayMenu();
      if (result.success) {
        setMenu(result.data);
      }
      setLoading(false);
    };

    fetchMenu();

    // Subscribe to menu updates
    const unsubscribe = menuService.subscribeToMenuUpdates((updatedMenu) => {
      const today = new Date().toISOString().split('T')[0];
      if (updatedMenu.menu_date === today) {
        setMenu(updatedMenu);
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  if (loading) return <div>Loading menu...</div>;
  if (!menu) return <div>No menu available for today</div>;

  return (
    <div>
      <h2>Today's Menu</h2>
      <div>
        <h3>Breakfast</h3>
        <p>{menu.breakfast_items || 'Not available'}</p>
      </div>
      <div>
        <h3>Lunch</h3>
        <p>{menu.lunch_items || 'Not available'}</p>
      </div>
      <div>
        <h3>Dinner</h3>
        <p>{menu.dinner_items || 'Not available'}</p>
      </div>
    </div>
  );
}
```

## Dashboard Statistics

### Monthly Stats Component

```typescript
import { useState, useEffect } from 'react';
import {
  depositsService,
  expensesService,
  mealsService
} from './services';
import { useAuth } from './contexts/AuthContext';

function MonthlyStats() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalDeposits: 0,
    totalExpenses: 0,
    mealStats: {
      total_breakfast: 0,
      total_lunch: 0,
      total_dinner: 0,
      total_guest_breakfast: 0,
      total_guest_lunch: 0,
      total_guest_dinner: 0
    }
  });

  useEffect(() => {
    const fetchStats = async () => {
      if (!user) return;

      const currentMonth = new Date().toISOString().slice(0, 7);

      // Fetch deposits
      const depositsResult = await depositsService.getTotalDepositsByUserAndMonth(
        user.id,
        currentMonth
      );

      // Fetch expenses (if manager)
      let totalExpenses = 0;
      if (user.role === 'manager') {
        const expensesResult = await expensesService.getTotalExpensesByMonth(currentMonth);
        if (expensesResult.success) {
          totalExpenses = expensesResult.data || 0;
        }
      }

      // Fetch meal stats
      const mealStatsResult = await mealsService.getMealStatsByUserAndMonth(
        user.id,
        currentMonth
      );

      setStats({
        totalDeposits: depositsResult.data || 0,
        totalExpenses,
        mealStats: mealStatsResult.data || {
          total_breakfast: 0,
          total_lunch: 0,
          total_dinner: 0,
          total_guest_breakfast: 0,
          total_guest_lunch: 0,
          total_guest_dinner: 0
        }
      });
    };

    fetchStats();
  }, [user]);

  return (
    <div>
      <h2>Monthly Statistics</h2>
      <div>
        <h3>Deposits</h3>
        <p>₹{stats.totalDeposits.toFixed(2)}</p>
      </div>
      {user?.role === 'manager' && (
        <div>
          <h3>Expenses</h3>
          <p>₹{stats.totalExpenses.toFixed(2)}</p>
        </div>
      )}
      <div>
        <h3>Meals This Month</h3>
        <p>Breakfast: {stats.mealStats.total_breakfast}</p>
        <p>Lunch: {stats.mealStats.total_lunch}</p>
        <p>Dinner: {stats.mealStats.total_dinner}</p>
      </div>
    </div>
  );
}
```

## Error Handling Pattern

### Generic API Hook

```typescript
import { useState, useCallback } from 'react';
import { ServiceResponse } from './services/supabase';
import toast from 'react-hot-toast';

export function useApiCall<T, Args extends any[]>(
  apiFunction: (...args: Args) => Promise<ServiceResponse<T>>,
  onSuccess?: (data: T) => void
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);

  const execute = useCallback(
    async (...args: Args) => {
      setLoading(true);
      setError(null);

      const result = await apiFunction(...args);

      if (result.success) {
        setData(result.data);
        if (onSuccess && result.data) {
          onSuccess(result.data);
        }
      } else {
        setError(result.error);
        toast.error(result.error || 'An error occurred');
      }

      setLoading(false);
      return result;
    },
    [apiFunction, onSuccess]
  );

  return { execute, loading, error, data };
}

// Usage:
function MyComponent() {
  const { execute: createDeposit, loading } = useApiCall(
    depositsService.createDeposit,
    (deposit) => {
      toast.success('Deposit created!');
      console.log('New deposit:', deposit);
    }
  );

  const handleSubmit = async () => {
    await createDeposit({
      user_id: 'user-id',
      amount: 1000,
      deposit_date: '2025-10-13',
      month: '2025-10',
      payment_method: 'cash'
    });
  };

  return <button onClick={handleSubmit} disabled={loading}>Submit</button>;
}
```

## Testing Services

```typescript
// Example test using vitest or jest
import { describe, it, expect, beforeAll } from 'vitest';
import { depositsService } from './services';

describe('Deposits Service', () => {
  let testDepositId: string;

  it('should create a deposit', async () => {
    const result = await depositsService.createDeposit({
      user_id: 'test-user-id',
      amount: 1000,
      deposit_date: '2025-10-13',
      month: '2025-10',
      payment_method: 'cash',
      notes: 'Test deposit'
    });

    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
    expect(result.data?.amount).toBe(1000);

    if (result.data) {
      testDepositId = result.data.id;
    }
  });

  it('should fetch deposits by user', async () => {
    const result = await depositsService.getDepositsByUser('test-user-id');

    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);
  });
});
```

## Best Practices Summary

1. **Always check `result.success`** before using data
2. **Use TypeScript types** for type safety
3. **Handle loading states** in UI
4. **Provide user feedback** with toasts or messages
5. **Clean up subscriptions** in useEffect cleanup
6. **Cache data** when appropriate to reduce API calls
7. **Implement proper error boundaries** in React
8. **Use custom hooks** to reduce code duplication
9. **Test services** independently from UI
10. **Monitor Supabase logs** for backend errors
