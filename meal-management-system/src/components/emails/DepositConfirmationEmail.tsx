import React from 'react';
import { EmailTemplateData } from '../../types/email.types';

export const generateDepositConfirmationHTML = (data: EmailTemplateData): string => {
  const {
    recipientName,
    depositAmount = 0,
    depositDate,
    paymentMethod,
    transactionId,
    currentBalance = 0,
  } = data;

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Deposit Confirmation</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5; }
    .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }
    .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
    .content { padding: 30px 20px; }
    .footer { background-color: #f9fafb; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; }
    .button { display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; }
    .alert-success { background-color: #d1fae5; border-left: 4px solid #10b981; color: #065f46; padding: 12px; border-radius: 6px; margin: 15px 0; }
    .info-box { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 15px; margin: 15px 0; }
    .info-row { display: table; width: 100%; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }
    .info-row:last-child { border-bottom: none; }
    .info-label { display: table-cell; font-weight: 600; color: #4b5563; width: 40%; }
    .info-value { display: table-cell; color: #111827; }
    .highlight-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }
    .amount { font-size: 36px; font-weight: 700; margin: 10px 0; }
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
              <h1>💰 Hostel Meal Management</h1>
            </td>
          </tr>
          <tr>
            <td class="content">
              <h2 style="color: #111827; margin-top: 0;">Deposit Confirmed!</h2>
              <p>Hi ${recipientName},</p>
              <p>Your deposit has been successfully recorded in the system.</p>

              <div class="alert-success">
                <p style="margin: 0;"><strong>✓ Payment Received</strong></p>
              </div>

              <div class="highlight-box">
                <p style="margin: 0; font-size: 14px; opacity: 0.9;">Deposit Amount</p>
                <div class="amount">₹${depositAmount.toFixed(2)}</div>
              </div>

              <div class="info-box">
                <div class="info-row">
                  <div class="info-label">Date:</div>
                  <div class="info-value">${depositDate}</div>
                </div>
                ${
                  paymentMethod
                    ? `<div class="info-row">
                        <div class="info-label">Payment Method:</div>
                        <div class="info-value">${paymentMethod.toUpperCase()}</div>
                      </div>`
                    : ''
                }
                ${
                  transactionId
                    ? `<div class="info-row">
                        <div class="info-label">Transaction ID:</div>
                        <div class="info-value">${transactionId}</div>
                      </div>`
                    : ''
                }
                <div class="info-row">
                  <div class="info-label">Current Balance:</div>
                  <div class="info-value" style="font-weight: 700; color: #16a34a;">₹${currentBalance.toFixed(2)}</div>
                </div>
              </div>

              <div style="text-align: center; margin: 30px 0;">
                <a href="{{app_url}}/deposits" class="button">View Deposit History</a>
              </div>

              <div class="divider"></div>
              <p style="font-size: 14px; color: #6b7280; margin-bottom: 0;">
                If you believe this is an error, please contact the hostel management immediately.
              </p>
            </td>
          </tr>
          <tr>
            <td class="footer">
              <p>This email was sent from Hostel Meal Management System<br>You're receiving this because you have deposit notifications enabled.</p>
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
