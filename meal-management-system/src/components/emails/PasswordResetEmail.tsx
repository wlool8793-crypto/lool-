import React from 'react';
import { EmailTemplateData } from '../../types/email.types';

export const generatePasswordResetEmailHTML = (data: EmailTemplateData): string => {
  const { recipientName, resetUrl, resetExpiry } = data;

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Password Reset Request</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5; }
    .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }
    .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
    .content { padding: 30px 20px; }
    .footer { background-color: #f9fafb; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; }
    .button { display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; }
    .alert-warning { background-color: #fef3c7; border-left: 4px solid #f59e0b; color: #92400e; padding: 12px; border-radius: 6px; margin: 15px 0; }
    .alert-danger { background-color: #fee2e2; border-left: 4px solid #ef4444; color: #991b1b; padding: 12px; border-radius: 6px; margin: 15px 0; }
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
              <h1>🔐 Hostel Meal Management</h1>
            </td>
          </tr>
          <tr>
            <td class="content">
              <h2 style="color: #111827; margin-top: 0;">Password Reset Request</h2>
              <p>Hi ${recipientName},</p>
              <p>We received a request to reset your password for your Hostel Meal Management account.</p>

              <div class="alert-warning">
                <p style="margin: 0;">If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
              </div>

              <p>Click the button below to reset your password:</p>

              <div style="text-align: center; margin: 30px 0;">
                <a href="${resetUrl || '#'}" class="button">Reset Password</a>
              </div>

              <p style="text-align: center; font-size: 14px; color: #6b7280;">
                Or copy and paste this link into your browser:
                <br>
                <a href="${resetUrl || '#'}" style="color: #667eea; word-break: break-all;">${resetUrl || '#'}</a>
              </p>

              <div class="alert-danger">
                <p style="margin: 0;"><strong>⚠ Security Notice:</strong></p>
                <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                  <li>This link will expire in ${resetExpiry || '1 hour'}</li>
                  <li>This link can only be used once</li>
                  <li>Never share this link with anyone</li>
                </ul>
              </div>

              <div class="divider"></div>
              <p style="font-size: 14px; color: #6b7280; margin-bottom: 0;">
                If you're having trouble with the button above, copy and paste the URL into your web browser.
              </p>
            </td>
          </tr>
          <tr>
            <td class="footer">
              <p>This email was sent from Hostel Meal Management System<br>This is an automated security email.</p>
              <p style="color: #dc2626; font-weight: 600;">If you didn't request a password reset, please contact support immediately.</p>
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
