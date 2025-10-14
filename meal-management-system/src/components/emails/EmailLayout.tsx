import React from 'react';

interface EmailLayoutProps {
  children: React.ReactNode;
  previewText?: string;
}

export const EmailLayout: React.FC<EmailLayoutProps> = ({ children, previewText }) => {
  return (
    <html>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Hostel Meal Management System</title>
        <style>{`
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
          }
          .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
          }
          .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
          }
          .header h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 600;
          }
          .content {
            padding: 30px 20px;
          }
          .footer {
            background-color: #f9fafb;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
          }
          .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 10px 0;
          }
          .button:hover {
            background-color: #5568d3;
          }
          .alert {
            padding: 12px;
            border-radius: 6px;
            margin: 15px 0;
          }
          .alert-info {
            background-color: #dbeafe;
            border-left: 4px solid #3b82f6;
            color: #1e40af;
          }
          .alert-warning {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            color: #92400e;
          }
          .alert-success {
            background-color: #d1fae5;
            border-left: 4px solid #10b981;
            color: #065f46;
          }
          .alert-danger {
            background-color: #fee2e2;
            border-left: 4px solid #ef4444;
            color: #991b1b;
          }
          .info-box {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
          }
          .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
          }
          .info-row:last-child {
            border-bottom: none;
          }
          .info-label {
            font-weight: 600;
            color: #4b5563;
          }
          .info-value {
            color: #111827;
          }
          .divider {
            height: 1px;
            background-color: #e5e7eb;
            margin: 20px 0;
          }
          .preview-text {
            display: none;
            font-size: 1px;
            line-height: 1px;
            max-height: 0;
            max-width: 0;
            opacity: 0;
            overflow: hidden;
          }
        `}</style>
      </head>
      <body>
        {previewText && <div className="preview-text">{previewText}</div>}
        <table role="presentation" width="100%" cellPadding="0" cellSpacing="0">
          <tr>
            <td align="center" style={{ padding: '20px 0' }}>
              <table className="container" role="presentation" width="600" cellPadding="0" cellSpacing="0">
                <tr>
                  <td className="header">
                    <h1>Hostel Meal Management</h1>
                  </td>
                </tr>
                <tr>
                  <td className="content">{children}</td>
                </tr>
                <tr>
                  <td className="footer">
                    <p>
                      This email was sent from Hostel Meal Management System
                      <br />
                      You're receiving this because you're registered in the system.
                    </p>
                    <p>
                      <a href="{{unsubscribe_url}}" style={{ color: '#6b7280', textDecoration: 'underline' }}>
                        Update email preferences
                      </a>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
  );
};
