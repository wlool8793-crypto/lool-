import { supabase, ServiceResponse, createSuccessResponse, createErrorResponse } from './supabase';
import {
  EmailPayload,
  EmailTemplateData,
  EmailTemplateType,
  EmailRecipient,
  EmailLog,
  InsertEmailLog,
  EmailServiceConfig,
  EmailValidationResult,
  BulkEmailRequest,
  EmailDeliveryStats,
} from '../types/email.types';
import {
  generateWelcomeEmailHTML,
  generateMealDeadlineReminderHTML,
  generateDepositConfirmationHTML,
  generateExpenseNotificationHTML,
  generateAnnouncementEmailHTML,
  generatePasswordResetEmailHTML,
} from '../components/emails';

/**
 * Email Service Configuration
 * This should be loaded from environment variables
 */
const getEmailConfig = (): EmailServiceConfig => {
  return {
    provider: (import.meta.env.VITE_EMAIL_PROVIDER || 'resend') as 'resend' | 'sendgrid' | 'supabase',
    apiKey: import.meta.env.VITE_EMAIL_API_KEY || '',
    fromEmail: import.meta.env.VITE_EMAIL_FROM || 'noreply@hostelmeal.com',
    fromName: import.meta.env.VITE_EMAIL_FROM_NAME || 'Hostel Meal Management',
    replyToEmail: import.meta.env.VITE_EMAIL_REPLY_TO || '',
    webhookSecret: import.meta.env.VITE_EMAIL_WEBHOOK_SECRET || '',
    enabled: import.meta.env.VITE_EMAIL_ENABLED !== 'false',
  };
};

/**
 * Generate HTML content for email template
 */
const generateEmailHTML = (template: EmailTemplateType, data: EmailTemplateData): string => {
  const appUrl = window.location.origin;
  const unsubscribeUrl = `${appUrl}/profile/email-preferences`;

  // Replace placeholders
  const replacePlaceholders = (html: string): string => {
    return html
      .replace(/\{\{app_url\}\}/g, appUrl)
      .replace(/\{\{unsubscribe_url\}\}/g, unsubscribeUrl);
  };

  switch (template) {
    case 'welcome':
      return replacePlaceholders(generateWelcomeEmailHTML(data));
    case 'meal_deadline_reminder':
      return replacePlaceholders(generateMealDeadlineReminderHTML(data));
    case 'deposit_confirmation':
      return replacePlaceholders(generateDepositConfirmationHTML(data));
    case 'expense_notification':
      return replacePlaceholders(generateExpenseNotificationHTML(data));
    case 'announcement_broadcast':
      return replacePlaceholders(generateAnnouncementEmailHTML(data));
    case 'password_reset':
      return replacePlaceholders(generatePasswordResetEmailHTML(data));
    default:
      throw new Error(`Unsupported email template: ${template}`);
  }
};

/**
 * Validate email payload
 */
const validateEmailPayload = (payload: EmailPayload): EmailValidationResult => {
  const errors: string[] = [];

  if (!payload.to) {
    errors.push('Recipient email is required');
  }

  if (Array.isArray(payload.to)) {
    if (payload.to.length === 0) {
      errors.push('At least one recipient is required');
    }
    payload.to.forEach((recipient, index) => {
      if (!recipient.email || !recipient.email.includes('@')) {
        errors.push(`Invalid email for recipient ${index + 1}`);
      }
    });
  } else {
    if (!payload.to.email || !payload.to.email.includes('@')) {
      errors.push('Invalid recipient email');
    }
  }

  if (!payload.subject || payload.subject.trim() === '') {
    errors.push('Email subject is required');
  }

  if (!payload.template) {
    errors.push('Email template is required');
  }

  if (!payload.templateData) {
    errors.push('Template data is required');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Send email using Resend API
 */
const sendEmailViaResend = async (payload: EmailPayload, htmlContent: string): Promise<any> => {
  const config = getEmailConfig();

  if (!config.apiKey) {
    throw new Error('Resend API key is not configured');
  }

  const recipients = Array.isArray(payload.to) ? payload.to : [payload.to];

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${config.apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: `${config.fromName} <${config.fromEmail}>`,
      to: recipients.map(r => r.email),
      reply_to: payload.replyTo || config.replyToEmail,
      subject: payload.subject,
      html: htmlContent,
      tags: payload.tags || [payload.template],
      ...(payload.attachments && { attachments: payload.attachments }),
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to send email via Resend');
  }

  return response.json();
};

/**
 * Send email using Supabase Edge Function
 */
const sendEmailViaSupabase = async (payload: EmailPayload, htmlContent: string): Promise<any> => {
  const { data, error } = await supabase.functions.invoke('send-email', {
    body: {
      ...payload,
      html: htmlContent,
    },
  });

  if (error) {
    throw error;
  }

  return data;
};

/**
 * Log email to database
 */
const logEmail = async (
  payload: EmailPayload,
  status: 'sent' | 'failed',
  error?: string
): Promise<void> => {
  try {
    const recipients = Array.isArray(payload.to) ? payload.to : [payload.to];

    const logs: InsertEmailLog[] = recipients.map(recipient => ({
      user_id: recipient.userId,
      recipient_email: recipient.email,
      template_type: payload.template,
      subject: payload.subject,
      status,
      error_message: error,
      metadata: payload.metadata,
      sent_at: status === 'sent' ? new Date().toISOString() : undefined,
    }));

    await supabase.from('email_logs').insert(logs);
  } catch (err) {
    console.error('Failed to log email:', err);
    // Don't throw error, just log it
  }
};

/**
 * Send a single email
 */
export const sendEmail = async (payload: EmailPayload): Promise<ServiceResponse<any>> => {
  try {
    const config = getEmailConfig();

    // Check if email service is enabled
    if (!config.enabled) {
      console.log('Email service is disabled. Email not sent:', payload.subject);
      return createSuccessResponse({ message: 'Email service is disabled' });
    }

    // Validate payload
    const validation = validateEmailPayload(payload);
    if (!validation.isValid) {
      return createErrorResponse(validation.errors.join(', '));
    }

    // Generate HTML content
    const htmlContent = generateEmailHTML(payload.template, payload.templateData);

    // Send email based on provider
    let result;
    if (config.provider === 'resend') {
      result = await sendEmailViaResend(payload, htmlContent);
    } else if (config.provider === 'supabase') {
      result = await sendEmailViaSupabase(payload, htmlContent);
    } else {
      throw new Error(`Unsupported email provider: ${config.provider}`);
    }

    // Log successful email
    await logEmail(payload, 'sent');

    return createSuccessResponse(result);
  } catch (error) {
    // Log failed email
    await logEmail(payload, 'failed', error instanceof Error ? error.message : 'Unknown error');

    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to send email'
    );
  }
};

/**
 * Send bulk emails
 */
export const sendBulkEmails = async (
  request: BulkEmailRequest
): Promise<ServiceResponse<EmailDeliveryStats>> => {
  try {
    const stats: EmailDeliveryStats = {
      total: request.recipients.length,
      sent: 0,
      failed: 0,
      pending: 0,
      cancelled: 0,
    };

    // Send emails in batches to avoid rate limiting
    const BATCH_SIZE = 10;
    for (let i = 0; i < request.recipients.length; i += BATCH_SIZE) {
      const batch = request.recipients.slice(i, i + BATCH_SIZE);

      const promises = batch.map(async (recipient) => {
        const individualData = request.individualData?.get(recipient.email);
        const templateData: EmailTemplateData = {
          ...request.templateData,
          ...individualData,
          recipientName: recipient.name,
          recipientEmail: recipient.email,
        };

        const payload: EmailPayload = {
          to: recipient,
          subject: request.templateData.announcementTitle || 'Hostel Meal Update',
          template: request.template,
          templateData,
          priority: request.priority,
          scheduledFor: request.scheduledFor,
        };

        const result = await sendEmail(payload);
        if (result.success) {
          stats.sent++;
        } else {
          stats.failed++;
        }
      });

      await Promise.all(promises);

      // Add delay between batches to avoid rate limiting
      if (i + BATCH_SIZE < request.recipients.length) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    return createSuccessResponse(stats);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to send bulk emails'
    );
  }
};

/**
 * Get email logs for a user
 */
export const getEmailLogs = async (userId: string): Promise<ServiceResponse<EmailLog[]>> => {
  try {
    const { data, error } = await supabase
      .from('email_logs')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(50);

    if (error) {
      return createErrorResponse(error.message);
    }

    return createSuccessResponse(data || []);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to fetch email logs'
    );
  }
};

/**
 * Get email delivery statistics
 */
export const getEmailStats = async (
  userId?: string,
  startDate?: string,
  endDate?: string
): Promise<ServiceResponse<EmailDeliveryStats>> => {
  try {
    let query = supabase.from('email_logs').select('status', { count: 'exact' });

    if (userId) {
      query = query.eq('user_id', userId);
    }

    if (startDate) {
      query = query.gte('created_at', startDate);
    }

    if (endDate) {
      query = query.lte('created_at', endDate);
    }

    const { data, error, count } = await query;

    if (error) {
      return createErrorResponse(error.message);
    }

    const stats: EmailDeliveryStats = {
      total: count || 0,
      sent: data?.filter(log => log.status === 'sent').length || 0,
      failed: data?.filter(log => log.status === 'failed').length || 0,
      pending: data?.filter(log => log.status === 'pending').length || 0,
      cancelled: data?.filter(log => log.status === 'cancelled').length || 0,
    };

    return createSuccessResponse(stats);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Failed to fetch email statistics'
    );
  }
};

/**
 * Test email configuration
 */
export const testEmailConfiguration = async (
  testEmail: string
): Promise<ServiceResponse<any>> => {
  try {
    const payload: EmailPayload = {
      to: { email: testEmail, name: 'Test User' },
      subject: 'Test Email from Hostel Meal Management',
      template: 'welcome',
      templateData: {
        recipientName: 'Test User',
        recipientEmail: testEmail,
        welcomeMessage: 'This is a test email to verify your email configuration.',
        loginUrl: window.location.origin,
      },
    };

    return await sendEmail(payload);
  } catch (error) {
    return createErrorResponse(
      error instanceof Error ? error.message : 'Email configuration test failed'
    );
  }
};
