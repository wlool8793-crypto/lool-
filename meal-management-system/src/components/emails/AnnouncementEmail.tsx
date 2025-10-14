import React from 'react';
import { EmailTemplateData } from '../../types/email.types';

export const generateAnnouncementEmailHTML = (data: EmailTemplateData): string => {
  const {
    recipientName,
    announcementTitle,
    announcementMessage,
    announcementPriority = 'medium',
    announcementDate,
  } = data;

  const priorityColors: Record<string, { bg: string; border: string; text: string }> = {
    high: { bg: '#fee2e2', border: '#ef4444', text: '#991b1b' },
    medium: { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' },
    low: { bg: '#f3f4f6', border: '#6b7280', text: '#374151' },
  };

  const priority = priorityColors[announcementPriority] || priorityColors.medium;

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hostel Announcement</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5; }
    .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }
    .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
    .content { padding: 30px 20px; }
    .footer { background-color: #f9fafb; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; }
    .button { display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; }
    .priority-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; }
    .announcement-box { background-color: #f9fafb; border-left: 4px solid; padding: 20px; border-radius: 6px; margin: 20px 0; }
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
              <h1>📢 Hostel Announcement</h1>
            </td>
          </tr>
          <tr>
            <td class="content">
              <p>Hi ${recipientName},</p>

              <div style="text-align: center; margin: 10px 0;">
                <span class="priority-badge" style="background-color: ${priority.bg}; color: ${priority.text}; border: 1px solid ${priority.border};">
                  ${announcementPriority} Priority
                </span>
              </div>

              <h2 style="color: #111827; margin: 20px 0; text-align: center;">${announcementTitle}</h2>

              <div class="announcement-box" style="border-color: ${priority.border}; background-color: ${priority.bg}; color: ${priority.text};">
                <div style="font-size: 16px; white-space: pre-line;">${announcementMessage}</div>
              </div>

              ${
                announcementDate
                  ? `<p style="text-align: center; font-size: 14px; color: #6b7280;">
                      <strong>Posted on:</strong> ${announcementDate}
                    </p>`
                  : ''
              }

              <div style="text-align: center; margin: 30px 0;">
                <a href="{{app_url}}/announcements" class="button">View All Announcements</a>
              </div>

              <div class="divider"></div>
              <p style="font-size: 14px; color: #6b7280; margin-bottom: 0;">
                This announcement was posted by hostel management.
              </p>
            </td>
          </tr>
          <tr>
            <td class="footer">
              <p>This email was sent from Hostel Meal Management System<br>You're receiving this because you have announcement notifications enabled.</p>
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
