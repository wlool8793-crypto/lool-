# Supabase Service Layer Documentation

This directory contains all the service layer functions for interacting with Supabase backend.

## Overview

All services follow a consistent pattern:
- TypeScript with proper typing from `database.types.ts`
- Consistent error handling
- Standardized response format using `ServiceResponse<T>`
- All async functions return promises
- Real-time subscription support where applicable

## Service Response Format

All service functions return a `ServiceResponse<T>` object:

```typescript
interface ServiceResponse<T> {
  data: T | null;
  error: string | null;
  success: boolean;
}
```

Example usage:
```typescript
const result = await mealsService.getMealsByUser(userId);
if (result.success) {
  console.log('Meals:', result.data);
} else {
  console.error('Error:', result.error);
}
```

## Services

### 1. supabase.ts
Core Supabase client initialization and helper functions.

```typescript
import { supabase } from './services/supabase';
```

### 2. auth.service.ts
Authentication and user management.

**Functions:**
- `login(credentials)` - Login with email/password
- `register(userData)` - Register new user
- `logout()` - Logout current user
- `getCurrentUser()` - Get current authenticated user profile
- `getSession()` - Get current session
- `resetPassword(email)` - Send password reset email
- `updatePassword(newPassword)` - Update user password
- `onAuthStateChange(callback)` - Listen to auth state changes

**Example:**
```typescript
import { authService } from './services';

// Login
const result = await authService.login({
  email: 'user@example.com',
  password: 'password123'
});

// Register
const registerResult = await authService.register({
  email: 'new@example.com',
  password: 'password123',
  full_name: 'John Doe',
  role: 'student',
  room_number: '101'
});
```

### 3. meals.service.ts
CRUD operations for meal entries.

**Functions:**
- `getMealsByUser(userId, startDate?, endDate?)` - Get meals for a user
- `getMealByUserAndDate(userId, mealDate)` - Get specific meal
- `getMealsByDate(mealDate)` - Get all meals for a date
- `getMealsByDateRange(startDate, endDate)` - Get meals in range
- `createMeal(meal)` - Create new meal entry
- `updateMeal(id, updates)` - Update meal entry
- `upsertMeal(meal)` - Create or update meal
- `deleteMeal(id)` - Delete meal entry
- `getMealStatsByUserAndMonth(userId, month)` - Get statistics
- `isMealLocked(userId, mealDate, mealType)` - Check if meal is locked
- `bulkUpdateMealLocks(mealDate, mealType, locked)` - Bulk update locks

**Example:**
```typescript
import { mealsService } from './services';

// Create/update meal
const result = await mealsService.upsertMeal({
  user_id: 'user-uuid',
  meal_date: '2025-10-13',
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
```

### 4. deposits.service.ts
CRUD operations for deposits.

**Functions:**
- `getDepositsByUser(userId)` - Get all deposits for user
- `getDepositsByUserAndMonth(userId, month)` - Get deposits by month
- `getDepositsByMonth(month)` - Get all deposits for month
- `getDepositsByDateRange(startDate, endDate)` - Get deposits in range
- `getDepositById(id)` - Get single deposit
- `createDeposit(deposit)` - Create new deposit
- `updateDeposit(id, updates)` - Update deposit
- `deleteDeposit(id)` - Delete deposit
- `getTotalDepositsByUserAndMonth(userId, month)` - Get total amount
- `getTotalDepositsByMonth(month)` - Get total for all users
- `getDepositStatsByPaymentMethod(month)` - Get stats by payment method
- `getRecentDeposits(limit)` - Get recent deposits
- `bulkCreateDeposits(deposits)` - Bulk create

**Example:**
```typescript
import { depositsService } from './services';

const result = await depositsService.createDeposit({
  user_id: 'user-uuid',
  amount: 5000,
  deposit_date: '2025-10-13',
  month: '2025-10',
  payment_method: 'upi',
  notes: 'Monthly deposit'
});
```

### 5. expenses.service.ts
CRUD operations for expenses.

**Functions:**
- `getExpensesByMonth(month)` - Get expenses for month
- `getExpensesByDateRange(startDate, endDate)` - Get expenses in range
- `getExpensesByCategory(month, category)` - Get by category
- `getExpenseById(id)` - Get single expense
- `createExpense(expense)` - Create new expense
- `updateExpense(id, updates)` - Update expense
- `deleteExpense(id)` - Delete expense
- `getTotalExpensesByMonth(month)` - Get total amount
- `getExpenseStatsByCategory(month)` - Get stats by category
- `getRecentExpenses(limit)` - Get recent expenses
- `getExpensesByRecorder(recordedBy, month?)` - Get by recorder
- `bulkCreateExpenses(expenses)` - Bulk create
- `uploadExpenseReceipt(file, expenseId)` - Upload receipt image
- `deleteExpenseReceipt(receiptUrl)` - Delete receipt

**Example:**
```typescript
import { expensesService } from './services';

const result = await expensesService.createExpense({
  amount: 2500,
  expense_date: '2025-10-13',
  month: '2025-10',
  category: 'vegetables',
  description: 'Weekly vegetable purchase',
  recorded_by: 'manager-uuid'
});
```

### 6. users.service.ts
User management operations.

**Functions:**
- `getAllUsers()` - Get all users
- `getUsersByRole(role)` - Get users by role
- `getActiveUsers()` - Get active users only
- `getUserById(id)` - Get user by ID
- `getUserByEmail(email)` - Get user by email
- `updateUserProfile(id, updates)` - Update profile
- `deactivateUser(id)` - Deactivate user
- `activateUser(id)` - Activate user
- `deleteUser(id)` - Delete user (hard delete)
- `searchUsers(searchTerm)` - Search by name/email
- `getUsersByRoom(roomNumber)` - Get users by room
- `uploadProfilePicture(file, userId)` - Upload profile picture
- `deleteProfilePicture(profilePictureUrl)` - Delete profile picture
- `getUserCountByRole()` - Get count by role
- `updateUserRole(userId, newRole)` - Update user role

**Example:**
```typescript
import { usersService } from './services';

const result = await usersService.updateUserProfile('user-uuid', {
  full_name: 'John Doe Updated',
  room_number: '102',
  phone: '+1234567890'
});
```

### 7. notifications.service.ts
Notification operations.

**Functions:**
- `getNotificationsByUser(userId)` - Get all notifications
- `getUnreadNotificationsByUser(userId)` - Get unread only
- `getUnreadNotificationCount(userId)` - Get unread count
- `getNotificationsByType(userId, type)` - Get by type
- `createNotification(notification)` - Create notification
- `createBroadcastNotification(notification)` - Create for all users
- `markNotificationAsRead(id)` - Mark as read
- `markAllNotificationsAsRead(userId)` - Mark all as read
- `deleteNotification(id)` - Delete notification
- `deleteReadNotifications(userId)` - Delete all read
- `bulkCreateNotifications(userIds, notificationData)` - Bulk create
- `subscribeToNotifications(userId, callback)` - Real-time updates
- `getRecentNotifications(userId, limit)` - Get recent

**Example:**
```typescript
import { notificationsService } from './services';

// Create notification
const result = await notificationsService.createNotification({
  user_id: 'user-uuid',
  title: 'Meal Reminder',
  message: 'Don\'t forget to mark your meals for tomorrow!',
  type: 'reminder',
  is_read: false
});

// Subscribe to real-time updates
const unsubscribe = notificationsService.subscribeToNotifications(
  'user-uuid',
  (notification) => {
    console.log('New notification:', notification);
  }
);
```

### 8. menu.service.ts
Menu management operations.

**Functions:**
- `getMenuByDate(menuDate)` - Get menu for date
- `getMenusByDateRange(startDate, endDate)` - Get menus in range
- `getUpcomingMenus(days)` - Get upcoming menus
- `getMenuById(id)` - Get menu by ID
- `createMenu(menu)` - Create new menu
- `updateMenu(id, updates)` - Update menu
- `upsertMenu(menu)` - Create or update menu
- `deleteMenu(id)` - Delete menu
- `deleteMenuByDate(menuDate)` - Delete by date
- `bulkCreateMenus(menus)` - Bulk create
- `getMenusByCreator(createdBy)` - Get by creator
- `getTodayMenu()` - Get today's menu
- `getTomorrowMenu()` - Get tomorrow's menu
- `menuExistsForDate(menuDate)` - Check if menu exists
- `subscribeToMenuUpdates(callback)` - Real-time updates

**Example:**
```typescript
import { menuService } from './services';

const result = await menuService.upsertMenu({
  menu_date: '2025-10-14',
  breakfast_items: 'Poha, Tea, Banana',
  lunch_items: 'Dal, Rice, Roti, Sabzi',
  dinner_items: 'Pulao, Raita, Papad',
  created_by: 'manager-uuid'
});
```

### 9. settings.service.ts
Meal settings operations.

**Functions:**
- `getSettingsByMonth(month)` - Get settings for month
- `getCurrentMonthSettings()` - Get current month settings
- `getAllSettings()` - Get all settings
- `getSettingsById(id)` - Get by ID
- `createSettings(settings)` - Create new settings
- `updateSettings(id, updates)` - Update settings
- `upsertSettings(settings)` - Create or update
- `deleteSettings(id)` - Delete settings
- `deleteSettingsByMonth(month)` - Delete by month
- `getOrCreateCurrentMonthSettings()` - Get or create with defaults
- `settingsExistForMonth(month)` - Check if exists
- `getSettingsByMonthRange(startMonth, endMonth)` - Get range
- `copySettingsToMonth(fromMonth, toMonth)` - Copy settings
- `subscribeToSettingsUpdates(callback)` - Real-time updates

**Example:**
```typescript
import { settingsService } from './services';

const result = await settingsService.upsertSettings({
  month: '2025-10',
  breakfast_deadline_hour: 20,
  lunch_deadline_hour: 9,
  dinner_deadline_hour: 15,
  dinner_deadline_previous_day: false,
  late_cancellation_penalty: 10,
  guest_meal_price: 50
});
```

### 10. announcements.service.ts
Announcement operations.

**Functions:**
- `getActiveAnnouncements()` - Get active (not expired)
- `getAllAnnouncements()` - Get all including expired
- `getAnnouncementsByPriority(priority)` - Get by priority
- `getHighPriorityAnnouncements()` - Get high priority only
- `getAnnouncementById(id)` - Get by ID
- `createAnnouncement(announcement)` - Create announcement
- `updateAnnouncement(id, updates)` - Update announcement
- `deleteAnnouncement(id)` - Delete announcement
- `getAnnouncementsByCreator(createdBy)` - Get by creator
- `getRecentAnnouncements(limit)` - Get recent
- `getExpiredAnnouncements()` - Get expired
- `extendAnnouncementExpiration(id, daysToAdd)` - Extend expiry
- `setAnnouncementNeverExpire(id)` - Never expire
- `deleteExpiredAnnouncements()` - Delete all expired
- `searchAnnouncements(searchTerm)` - Search announcements
- `subscribeToAnnouncements(callback)` - Real-time updates

**Example:**
```typescript
import { announcementsService } from './services';

const result = await announcementsService.createAnnouncement({
  title: 'Important Notice',
  message: 'Mess will be closed on Sunday for maintenance.',
  priority: 'high',
  created_by: 'manager-uuid',
  expires_at: '2025-10-20T23:59:59Z'
});
```

## Environment Variables

Make sure to set up the following environment variables in your `.env` file:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Error Handling

All services use try-catch blocks and return consistent error responses:

```typescript
if (!result.success) {
  // Handle error
  console.error(result.error);
  toast.error(result.error);
  return;
}

// Use data
const data = result.data;
```

## Real-time Subscriptions

Services that support real-time updates (notifications, menu, settings, announcements) return an unsubscribe function:

```typescript
const unsubscribe = notificationsService.subscribeToNotifications(
  userId,
  (notification) => {
    // Handle new notification
  }
);

// Later, when component unmounts
unsubscribe();
```

## Best Practices

1. Always check `result.success` before using `result.data`
2. Handle errors appropriately with user feedback
3. Use TypeScript types from `database.types.ts`
4. Unsubscribe from real-time listeners when components unmount
5. Use bulk operations when possible for better performance
6. Implement proper loading states in UI
7. Cache frequently accessed data when appropriate

## File Upload Services

For uploading files (receipts, profile pictures):

```typescript
// Upload expense receipt
const file = event.target.files[0];
const uploadResult = await expensesService.uploadExpenseReceipt(file, expenseId);
if (uploadResult.success) {
  const receiptUrl = uploadResult.data;
  // Update expense with receipt URL
  await expensesService.updateExpense(expenseId, { receipt_url: receiptUrl });
}

// Upload profile picture
const uploadResult = await usersService.uploadProfilePicture(file, userId);
if (uploadResult.success) {
  const profilePictureUrl = uploadResult.data;
  await usersService.updateUserProfile(userId, {
    profile_picture_url: profilePictureUrl
  });
}
```

## Testing

To test services, ensure:
1. Supabase project is set up with correct schema
2. Environment variables are configured
3. RLS (Row Level Security) policies are properly set
4. User has appropriate permissions

## Support

For issues or questions:
1. Check Supabase dashboard for database errors
2. Verify RLS policies
3. Check browser console for detailed error messages
4. Review Supabase logs for backend errors
