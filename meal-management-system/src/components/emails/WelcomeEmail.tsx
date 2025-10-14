import React from 'react';
import { EmailLayout } from './EmailLayout';
import { EmailTemplateData } from '../../types/email.types';

interface WelcomeEmailProps {
  data: EmailTemplateData;
}

export const WelcomeEmail: React.FC<WelcomeEmailProps> = ({ data }) => {
  const { recipientName, loginUrl, welcomeMessage } = data;

  return (
    <EmailLayout previewText={`Welcome to Hostel Meal Management, ${recipientName}!`}>
      <h2 style={{ color: '#111827', marginTop: 0 }}>Welcome, {recipientName}!</h2>

      <p>
        We're excited to have you join the Hostel Meal Management System. Your account has been successfully created.
      </p>

      {welcomeMessage && (
        <div className="alert alert-info">
          <p style={{ margin: 0 }}>{welcomeMessage}</p>
        </div>
      )}

      <div className="info-box">
        <h3 style={{ marginTop: 0, color: '#4b5563' }}>What you can do:</h3>
        <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
          <li>Select your daily meals (breakfast, lunch, dinner)</li>
          <li>View the weekly menu</li>
          <li>Track your meal expenses and deposits</li>
          <li>Receive deadline reminders</li>
          <li>Stay updated with hostel announcements</li>
        </ul>
      </div>

      <div style={{ textAlign: 'center', margin: '30px 0' }}>
        <a href={loginUrl || '#'} className="button">
          Login to Your Account
        </a>
      </div>

      <p style={{ fontSize: '14px', color: '#6b7280' }}>
        <strong>Important:</strong> Remember to select your meals before the deadlines to avoid penalties.
      </p>

      <div className="divider"></div>

      <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: 0 }}>
        If you have any questions, please contact the hostel management.
      </p>
    </EmailLayout>
  );
};

// Export HTML string generator for use in email service
export const generateWelcomeEmailHTML = (data: EmailTemplateData): string => {
  const { recipientName, loginUrl, welcomeMessage } = data;

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to Hostel Meal Management</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5; }
    .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }
    .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
    .content { padding: 30px 20px; }
    .footer { background-color: #f9fafb; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; }
    .button { display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; }
    .alert-info { background-color: #dbeafe; border-left: 4px solid #3b82f6; color: #1e40af; padding: 12px; border-radius: 6px; margin: 15px 0; }
    .info-box { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 15px; margin: 15px 0; }
    .divider { height: 1px; background-color: #e5e7eb; margin: 20px 0; }
  </style>
</head>
<body>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding: 20px 0;">
        <table class="container" role="presentation" width="600" cellpadding="0" cellspacing="0">
          <tr>
            <td class="header">
              <h1>Hostel Meal Management</h1>
            </td>
          </tr>
          <tr>
            <td class="content">
              <h2 style="color: #111827; margin-top: 0;">Welcome, ${recipientName}!</h2>
              <p>We're excited to have you join the Hostel Meal Management System. Your account has been successfully created.</p>
              ${welcomeMessage ? `<div class="alert-info"><p style="margin: 0;">${welcomeMessage}</p></div>` : ''}
              <div class="info-box">
                <h3 style="margin-top: 0; color: #4b5563;">What you can do:</h3>
                <ul style="margin-bottom: 0; padding-left: 20px;">
                  <li>Select your daily meals (breakfast, lunch, dinner)</li>
                  <li>View the weekly menu</li>
                  <li>Track your meal expenses and deposits</li>
                  <li>Receive deadline reminders</li>
                  <li>Stay updated with hostel announcements</li>
                </ul>
              </div>
              <div style="text-align: center; margin: 30px 0;">
                <a href="${loginUrl || '#'}" class="button">Login to Your Account</a>
              </div>
              <p style="font-size: 14px; color: #6b7280;"><strong>Important:</strong> Remember to select your meals before the deadlines to avoid penalties.</p>
              <div class="divider"></div>
              <p style="font-size: 14px; color: #6b7280; margin-bottom: 0;">If you have any questions, please contact the hostel management.</p>
            </td>
          </tr>
          <tr>
            <td class="footer">
              <p>This email was sent from Hostel Meal Management System<br>You're receiving this because you're registered in the system.</p>
              <p><a href="{{unsubscribe_url}}" style="color: #6b7280; text-decoration: underline;">Update email preferences</a></p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `.trim();
};
