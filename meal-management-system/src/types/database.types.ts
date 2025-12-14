// Database types matching Supabase schema

export type UserRole = 'manager' | 'student';
export type PaymentMethod = 'cash' | 'online' | 'upi';
export type ExpenseCategory = 'vegetables' | 'rice' | 'meat' | 'spices' | 'gas' | 'utilities' | 'other';
export type NotificationType = 'reminder' | 'warning' | 'info' | 'alert';
export type Priority = 'low' | 'medium' | 'high';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  full_name: string;
  room_number?: string;
  phone?: string;
  profile_picture_url?: string;
  is_active: boolean;
  email_notifications_enabled?: boolean;
  meal_reminders?: boolean;
  deposit_confirmations?: boolean;
  expense_notifications?: boolean;
  announcements?: boolean;
  daily_summaries?: boolean;
  monthly_reports?: boolean;
  reminder_hours_before?: number;
  created_at: string;
  updated_at: string;
}

export interface Deposit {
  id: string;
  user_id: string;
  amount: number;
  deposit_date: string;
  month: string;
  payment_method?: PaymentMethod;
  notes?: string;
  recorded_by?: string;
  created_at: string;
}

export interface Meal {
  id: string;
  user_id: string;
  meal_date: string;
  breakfast: boolean;
  lunch: boolean;
  dinner: boolean;
  breakfast_locked: boolean;
  lunch_locked: boolean;
  dinner_locked: boolean;
  guest_breakfast: number;
  guest_lunch: number;
  guest_dinner: number;
  created_at: string;
  updated_at: string;
}

export interface Expense {
  id: string;
  amount: number;
  expense_date: string;
  month: string;
  category?: ExpenseCategory;
  description: string;
  receipt_url?: string;
  recorded_by?: string;
  created_at: string;
}

export interface MealSettings {
  id: string;
  month: string;
  breakfast_deadline_hour: number;
  lunch_deadline_hour: number;
  dinner_deadline_hour: number;
  dinner_deadline_previous_day: boolean;
  fixed_meal_cost?: number;
  late_cancellation_penalty: number;
  guest_meal_price?: number;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  user_id?: string;
  title: string;
  message: string;
  type?: NotificationType;
  is_read: boolean;
  created_at: string;
}

export interface Menu {
  id: string;
  menu_date: string;
  breakfast_items?: string;
  lunch_items?: string;
  dinner_items?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface Announcement {
  id: string;
  title: string;
  message: string;
  priority: Priority;
  created_by?: string;
  created_at: string;
  expires_at?: string;
}

// Insert types (without auto-generated fields)
export type InsertUser = Omit<User, 'created_at' | 'updated_at'>;
export type InsertDeposit = Omit<Deposit, 'id' | 'created_at'>;
export type InsertMeal = Omit<Meal, 'id' | 'created_at' | 'updated_at'>;
export type InsertExpense = Omit<Expense, 'id' | 'created_at'>;
export type InsertMealSettings = Omit<MealSettings, 'id' | 'created_at' | 'updated_at'>;
export type InsertNotification = Omit<Notification, 'id' | 'created_at'>;
export type InsertMenu = Omit<Menu, 'id' | 'created_at' | 'updated_at'>;
export type InsertAnnouncement = Omit<Announcement, 'id' | 'created_at'>;

// Update types (all fields optional except id)
export type UpdateUser = Partial<User> & { id: string };
export type UpdateDeposit = Partial<Deposit> & { id: string };
export type UpdateMeal = Partial<Meal> & { id: string };
export type UpdateExpense = Partial<Expense> & { id: string };
export type UpdateMealSettings = Partial<MealSettings> & { id: string };
export type UpdateNotification = Partial<Notification> & { id: string };
export type UpdateMenu = Partial<Menu> & { id: string };
export type UpdateAnnouncement = Partial<Announcement> & { id: string };
