import React from 'react';
import { EmailTemplateData } from '../../types/email.types';

export const generateExpenseNotificationHTML = (data: EmailTemplateData): string => {
  const {
    recipientName,
    expenseAmount = 0,
    expenseDate,
    expenseCategory,
    expenseDescription,
    totalMonthlyExpenses = 0,
  } = data;

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Expense Notification</title>
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
    .info-row { display: table; width: 100%; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }
    .info-row:last-child { border-bottom: none; }
    .info-label { display: table-cell; font-weight: 600; color: #4b5563; width: 40%; }
    .info-value { display: table-cell; color: #111827; }
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
              <h1>📊 Hostel Meal Management</h1>
            </td>
          </tr>
          <tr>
            <td class="content">
              <h2 style="color: #111827; margin-top: 0;">New Expense Recorded</h2>
              <p>Hi ${recipientName},</p>
              <p>A new expense has been added to the hostel meal fund for transparency.</p>

              <div class="alert-info">
                <p style="margin: 0;"><strong>Expense Category:</strong> ${expenseCategory || 'General'}</p>
              </div>

              <div class="info-box">
                <div class="info-row">
                  <div class="info-label">Amount:</div>
                  <div class="info-value" style="font-weight: 700; color: #dc2626;">₹${expenseAmount.toFixed(2)}</div>
                </div>
                <div class="info-row">
                  <div class="info-label">Date:</div>
                  <div class="info-value">${expenseDate}</div>
                </div>
                ${
                  expenseDescription
                    ? `<div class="info-row">
                        <div class="info-label">Description:</div>
                        <div class="info-value">${expenseDescription}</div>
                      </div>`
                    : ''
                }
                <div class="info-row">
                  <div class="info-label">Monthly Total:</div>
                  <div class="info-value" style="font-weight: 700;">₹${totalMonthlyExpenses.toFixed(2)}</div>
                </div>
              </div>

              <div style="background-color: #fef3c7; padding: 15px; border-radius: 6px; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #92400e;">
                  <strong>💡 Transparency Notice:</strong> All expenses are shared with students to maintain transparency in meal cost calculations.
                </p>
              </div>

              <div style="text-align: center; margin: 30px 0;">
                <a href="{{app_url}}/expenses" class="button">View All Expenses</a>
              </div>

              <div class="divider"></div>
              <p style="font-size: 14px; color: #6b7280; margin-bottom: 0;">
                This expense will be included in the monthly cost calculation.
              </p>
            </td>
          </tr>
          <tr>
            <td class="footer">
              <p>This email was sent from Hostel Meal Management System<br>You're receiving this because you have expense notifications enabled.</p>
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
