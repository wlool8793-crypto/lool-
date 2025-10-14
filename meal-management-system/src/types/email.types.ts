// Email service types and interfaces

export type EmailTemplateType =
  | 'welcome'
  | 'password_reset'
  | 'meal_deadline_reminder'
  | 'deposit_confirmation'
  | 'expense_notification'
  | 'announcement_broadcast'
  | 'daily_summary'
  | 'monthly_report';

export type EmailPriority = 'high' | 'normal' | 'low';

export type EmailStatus = 'pending' | 'processing' | 'sent' | 'failed' | 'cancelled';

export interface EmailPreferences {
  email_notifications_enabled: boolean;
  meal_reminders: boolean;
  deposit_confirmations: boolean;
  expense_notifications: boolean;
  announcements: boolean;
  daily_summaries: boolean;
  monthly_reports: boolean;
  reminder_hours_before: number; // Hours before deadline to send reminder
}

export interface EmailRecipient {
  email: string;
  name: string;
  userId?: string;
}

export interface EmailAttachment {
  filename: string;
  content: string; // Base64 encoded content
  contentType: string;
}

export interface EmailTemplateData {
  // Common fields
  recipientName: string;
  recipientEmail: string;

  // Welcome email
  welcomeMessage?: string;
  loginUrl?: string;

  // Password reset
  resetToken?: string;
  resetUrl?: string;
  resetExpiry?: string;

  // Meal deadline reminder
  mealType?: 'breakfast' | 'lunch' | 'dinner';
  deadlineTime?: string;
  deadlineDate?: string;
  currentSelection?: boolean;
  menuItems?: string;

  // Deposit confirmation
  depositAmount?: number;
  depositDate?: string;
  paymentMethod?: string;
  transactionId?: string;
  currentBalance?: number;

  // Expense notification
  expenseAmount?: number;
  expenseDate?: string;
  expenseCategory?: string;
  expenseDescription?: string;
  totalMonthlyExpenses?: number;

  // Announcement
  announcementTitle?: string;
  announcementMessage?: string;
  announcementPriority?: string;
  announcementDate?: string;

  // Daily summary
  todayDate?: string;
  breakfastCount?: number;
  lunchCount?: number;
  dinnerCount?: number;
  totalDeposits?: number;
  totalExpenses?: number;

  // Monthly report
  month?: string;
  totalMeals?: number;
  totalCost?: number;
  averageDailyCost?: number;
  depositsThisMonth?: number;
  expensesThisMonth?: number;
  balance?: number;
}

export interface EmailPayload {
  to: EmailRecipient | EmailRecipient[];
  from?: EmailRecipient;
  replyTo?: string;
  subject: string;
  template: EmailTemplateType;
  templateData: EmailTemplateData;
  priority?: EmailPriority;
  attachments?: EmailAttachment[];
  tags?: string[];
  metadata?: Record<string, any>;
  scheduledFor?: Date;
}

export interface EmailQueueItem {
  id: string;
  payload: EmailPayload;
  status: EmailStatus;
  attempts: number;
  maxAttempts: number;
  error?: string;
  createdAt: Date;
  updatedAt: Date;
  sentAt?: Date;
  scheduledFor?: Date;
}

export interface EmailLog {
  id: string;
  user_id?: string;
  recipient_email: string;
  template_type: EmailTemplateType;
  subject: string;
  status: EmailStatus;
  error_message?: string;
  metadata?: Record<string, any>;
  sent_at?: string;
  created_at: string;
}

export interface EmailServiceConfig {
  provider: 'resend' | 'sendgrid' | 'supabase';
  apiKey: string;
  fromEmail: string;
  fromName: string;
  replyToEmail?: string;
  webhookSecret?: string;
  enabled: boolean;
}

export interface EmailValidationResult {
  isValid: boolean;
  errors: string[];
}

export interface BulkEmailRequest {
  recipients: EmailRecipient[];
  template: EmailTemplateType;
  templateData: Partial<EmailTemplateData>; // Common data for all recipients
  individualData?: Map<string, Partial<EmailTemplateData>>; // Individual data per recipient
  priority?: EmailPriority;
  scheduledFor?: Date;
}

export interface EmailDeliveryStats {
  total: number;
  sent: number;
  failed: number;
  pending: number;
  cancelled: number;
}

// Insert types for database
export type InsertEmailLog = Omit<EmailLog, 'id' | 'created_at'>;
