import React from 'react';
import { EmailTemplateData } from '../../types/email.types';

interface MealDeadlineReminderEmailProps {
  data: EmailTemplateData;
}

export const MealDeadlineReminderEmail: React.FC<MealDeadlineReminderEmailProps> = ({ data }) => {
  return null; // This component is for type checking only
};

export const generateMealDeadlineReminderHTML = (data: EmailTemplateData): string => {
  const {
    recipientName,
    mealType = 'breakfast',
    deadlineTime,
    deadlineDate,
    currentSelection = false,
    menuItems,
  } = data;

  const mealTypeCapitalized = mealType.charAt(0).toUpperCase() + mealType.slice(1);
  const mealEmoji = mealType === 'breakfast' ? '🍳' : mealType === 'lunch' ? '🍱' : '🍽️';

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${mealTypeCapitalized} Deadline Reminder</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5; }
    .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }
    .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
    .content { padding: 30px 20px; }
    .footer { background-color: #f9fafb; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; }
    .button { display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; }
    .alert-warning { background-color: #fef3c7; border-left: 4px solid #f59e0b; color: #92400e; padding: 12px; border-radius: 6px; margin: 15px 0; }
    .alert-success { background-color: #d1fae5; border-left: 4px solid #10b981; color: #065f46; padding: 12px; border-radius: 6px; margin: 15px 0; }
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
              <h1>${mealEmoji} Hostel Meal Management</h1>
            </td>
          </tr>
          <tr>
            <td class="content">
              <h2 style="color: #111827; margin-top: 0;">Hi ${recipientName},</h2>
              <p style="font-size: 16px;">This is a friendly reminder about the upcoming ${mealType} deadline.</p>

              ${
                currentSelection
                  ? `<div class="alert-success">
                      <p style="margin: 0;"><strong>✓ You have selected ${mealType}</strong> for ${deadlineDate}</p>
                    </div>`
                  : `<div class="alert-warning">
                      <p style="margin: 0;"><strong>⚠ You haven't selected ${mealType}</strong> for ${deadlineDate} yet!</p>
                    </div>`
              }

              <div class="info-box">
                <div class="info-row">
                  <div class="info-label">Meal:</div>
                  <div class="info-value">${mealTypeCapitalized}</div>
                </div>
                <div class="info-row">
                  <div class="info-label">Date:</div>
                  <div class="info-value">${deadlineDate}</div>
                </div>
                <div class="info-row">
                  <div class="info-label">Deadline:</div>
                  <div class="info-value">${deadlineTime}</div>
                </div>
                ${
                  menuItems
                    ? `<div class="info-row">
                        <div class="info-label">Menu:</div>
                        <div class="info-value">${menuItems}</div>
                      </div>`
                    : ''
                }
              </div>

              ${
                !currentSelection
                  ? `<div style="text-align: center; margin: 30px 0;">
                      <a href="{{app_url}}/meals" class="button">Select Your Meal Now</a>
                    </div>
                    <p style="font-size: 14px; color: #dc2626; text-align: center;">
                      <strong>Important:</strong> Selections made after the deadline may incur a penalty!
                    </p>`
                  : `<div style="text-align: center; margin: 30px 0;">
                      <a href="{{app_url}}/meals" class="button">View/Modify Selection</a>
                    </div>
                    <p style="font-size: 14px; color: #16a34a; text-align: center;">
                      You can still modify your selection before the deadline.
                    </p>`
              }

              <div class="divider"></div>
              <p style="font-size: 14px; color: #6b7280; margin-bottom: 0;">
                This is an automated reminder based on your email preferences.
              </p>
            </td>
          </tr>
          <tr>
            <td class="footer">
              <p>This email was sent from Hostel Meal Management System<br>You're receiving this because you have meal reminders enabled.</p>
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
