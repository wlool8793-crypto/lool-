# Quick Start Guide - Supabase Services

Get up and running with the service layer in 5 minutes!

## Step 1: Environment Setup (1 min)

Create a `.env` file in the project root:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

## Step 2: Import Services (30 sec)

```typescript
// Import all services at once
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

// Or import specific services
import { authService } from './services';
```

## Step 3: Basic Usage (2 min)

### Authentication
```typescript
// Login
const result = await authService.login({
  email: 'user@example.com',
  password: 'password123'
});

if (result.success) {
  console.log('Logged in as:', result.data.email);
} else {
  console.error('Login failed:', result.error);
}
```

### Fetch Data
```typescript
// Get user's meals
const meals = await mealsService.getMealsByUser(userId);

// Get today's menu
const menu = await menuService.getTodayMenu();

// Get notifications
const notifications = await notificationsService.getNotificationsByUser(userId);
```

### Create Data
```typescript
// Mark meals
await mealsService.upsertMeal({
  user_id: userId,
  meal_date: '2025-10-14',
  breakfast: true,
  lunch: true,
  dinner: false,
  breakfast_locked: false,
  lunch_locked: false,
  dinner_locked: false,
  guest_breakfast: 0,
  guest_lunch: 1,
  guest_dinner: 0
});

// Add deposit
await depositsService.createDeposit({
  user_id: userId,
  amount: 5000,
  deposit_date: '2025-10-13',
  month: '2025-10',
  payment_method: 'upi'
});
```

## Step 4: React Integration (1.5 min)

### Basic Hook Pattern
```typescript
import { useState, useEffect } from 'react';
import { mealsService } from './services';

function MyComponent() {
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMeals = async () => {
      const result = await mealsService.getMealsByUser(userId);
      if (result.success) {
        setMeals(result.data);
      }
      setLoading(false);
    };
    fetchMeals();
  }, [userId]);

  if (loading) return <div>Loading...</div>;

  return <div>{/* Render meals */}</div>;
}
```

### With Real-time Updates
```typescript
useEffect(() => {
  // Fetch initial data
  const fetchNotifications = async () => {
    const result = await notificationsService.getNotificationsByUser(userId);
    if (result.success) setNotifications(result.data);
  };
  fetchNotifications();

  // Subscribe to updates
  const unsubscribe = notificationsService.subscribeToNotifications(
    userId,
    (newNotification) => {
      setNotifications(prev => [newNotification, ...prev]);
    }
  );

  return unsubscribe; // Cleanup on unmount
}, [userId]);
```

## Common Patterns

### Error Handling
```typescript
const result = await mealsService.createMeal(mealData);

if (!result.success) {
  toast.error(result.error); // Show error to user
  return;
}

// Success - use result.data
console.log('Created meal:', result.data);
```

### Loading States
```typescript
const [loading, setLoading] = useState(false);

const handleSubmit = async () => {
  setLoading(true);
  const result = await depositsService.createDeposit(data);
  setLoading(false);

  if (result.success) {
    toast.success('Deposit created!');
  }
};

return (
  <button onClick={handleSubmit} disabled={loading}>
    {loading ? 'Submitting...' : 'Submit'}
  </button>
);
```

### Form Submission
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  const result = await expensesService.createExpense({
    amount: parseFloat(formData.amount),
    expense_date: formData.date,
    month: formData.date.slice(0, 7),
    category: formData.category,
    description: formData.description,
    recorded_by: userId
  });

  if (result.success) {
    toast.success('Expense added!');
    resetForm();
  } else {
    toast.error(result.error);
  }
};
```

## Service Cheat Sheet

| Task | Service | Function |
|------|---------|----------|
| Login | `authService` | `login(credentials)` |
| Get current user | `authService` | `getCurrentUser()` |
| Mark meals | `mealsService` | `upsertMeal(meal)` |
| Get user meals | `mealsService` | `getMealsByUser(userId)` |
| Add deposit | `depositsService` | `createDeposit(deposit)` |
| Get deposits | `depositsService` | `getDepositsByUser(userId)` |
| Add expense | `expensesService` | `createExpense(expense)` |
| Get expenses | `expensesService` | `getExpensesByMonth(month)` |
| Get today's menu | `menuService` | `getTodayMenu()` |
| Get notifications | `notificationsService` | `getNotificationsByUser(userId)` |
| Get settings | `settingsService` | `getCurrentMonthSettings()` |
| Get announcements | `announcementsService` | `getActiveAnnouncements()` |

## Response Format

All services return this format:
```typescript
{
  success: boolean;    // true if operation succeeded
  data: T | null;      // The data if successful
  error: string | null; // Error message if failed
}
```

Always check `success` before using `data`:
```typescript
const result = await someService.someFunction();
if (result.success) {
  // Use result.data safely
} else {
  // Handle result.error
}
```

## File Uploads

### Upload Profile Picture
```typescript
const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  if (!file) return;

  const uploadResult = await usersService.uploadProfilePicture(file, userId);
  if (uploadResult.success) {
    await usersService.updateUserProfile(userId, {
      profile_picture_url: uploadResult.data
    });
    toast.success('Profile picture updated!');
  }
};
```

### Upload Expense Receipt
```typescript
const file = e.target.files?.[0];
const uploadResult = await expensesService.uploadExpenseReceipt(file, expenseId);
if (uploadResult.success) {
  await expensesService.updateExpense(expenseId, {
    receipt_url: uploadResult.data
  });
}
```

## Troubleshooting

### "Missing Supabase environment variables"
- Check your `.env` file exists
- Ensure variables start with `VITE_`
- Restart dev server after adding variables

### "No rows returned" or null data
- This is normal when no data exists yet
- Check if `result.success` is true
- Data might be `null` legitimately

### RLS Policy Error
- Set up Row Level Security policies in Supabase
- Verify user has correct permissions
- Check Supabase dashboard for policy errors

### Real-time not working
- Ensure Realtime is enabled in Supabase project
- Check if subscription is cleaned up properly
- Verify table has REPLICA IDENTITY set

## Next Steps

1. ✅ Environment variables configured
2. ✅ Services imported
3. ✅ Basic usage working
4. ✅ React integration done

**Now explore:**
- 📖 See README.md for full API reference
- 💡 Check EXAMPLES.md for complete component examples
- 📋 Read IMPLEMENTATION_SUMMARY.md for overview

## Common Mistakes to Avoid

❌ **Don't** forget to check `result.success`
✅ **Do** always check before using `result.data`

❌ **Don't** use data without checking
```typescript
const meals = result.data.map(...) // ❌ Might crash
```
✅ **Do** check first
```typescript
if (result.success && result.data) {
  const meals = result.data.map(...) // ✅ Safe
}
```

❌ **Don't** forget to unsubscribe from real-time
```typescript
useEffect(() => {
  const unsubscribe = service.subscribe(...);
  // ❌ Missing cleanup
}, []);
```
✅ **Do** return cleanup function
```typescript
useEffect(() => {
  const unsubscribe = service.subscribe(...);
  return unsubscribe; // ✅ Proper cleanup
}, []);
```

## Getting Help

- **Service Documentation**: `README.md`
- **Code Examples**: `EXAMPLES.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Supabase Docs**: https://supabase.com/docs
- **TypeScript Types**: `src/types/database.types.ts`

## Quick Test

Test if everything works:

```typescript
import { authService } from './services';

// Check if Supabase client is initialized
console.log('Supabase initialized:', !!authService);

// Try to get session (won't fail even if no user logged in)
const result = await authService.getSession();
console.log('Session check successful:', result.success);
```

If both log `true`, you're ready to go! 🎉
