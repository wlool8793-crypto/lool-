import { ShareableLinkManager, ShareableLink } from './shareableLinkManager';
import { PrivacyManager, PrivacyConfig } from './privacyManager';

export interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  htmlTemplate: string;
  textTemplate: string;
  variables: string[];
  category: 'cv' | 'marriage' | 'general';
  isDefault: boolean;
}

export interface EmailShareOptions {
  recipients: string[];
  templateId?: string;
  customMessage?: string;
  attachments?: EmailAttachment[];
  tracking?: {
    enabled: boolean;
    uniqueId?: string;
  };
  scheduling?: {
    sendAt?: Date;
    timezone?: string;
  };
  privacy?: PrivacyConfig;
}

export interface EmailAttachment {
  filename: string;
  content: Blob | File;
  mimeType: string;
  size: number;
}

export interface EmailAnalytics {
  emailId: string;
  sentAt: Date;
  recipients: string[];
  delivered: number;
  opened: number;
  clicked: number;
  bounced: number;
  unsubscribed: number;
  trackingData: EmailTracking[];
}

export interface EmailTracking {
  id: string;
  timestamp: Date;
  action: 'sent' | 'delivered' | 'opened' | 'clicked' | 'bounced' | 'unsubscribed';
  recipient: string;
  ipAddress?: string;
  userAgent?: string;
  location?: string;
  deviceType?: string;
}

export interface BulkEmailOptions {
  campaignName: string;
  recipients: string[];
  templateId: string;
  variables?: Record<string, any>[];
  scheduling?: {
    batchSize?: number;
    delayBetweenBatches?: number;
    sendAt?: Date;
  };
  tracking?: {
    enabled: boolean;
    uniqueLinks?: boolean;
  };
}

export class EmailSharing {
  private static readonly TEMPLATES: EmailTemplate[] = [
    {
      id: 'cv_share',
      name: 'CV Share',
      subject: '{{firstName}}, here\'s my CV for {{position}}',
      category: 'cv',
      isDefault: true,
      variables: ['firstName', 'position', 'senderName', 'company'],
      htmlTemplate: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px;">
            <h1 style="margin: 0; font-size: 28px;">Professional CV</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">{{senderName}}</p>
          </div>

          <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-top: 0;">Hi {{firstName}},</h2>

            <p style="color: #666; line-height: 1.6;">
              I hope this email finds you well. I'm writing to share my updated CV with you regarding the {{position}} opportunity.
            </p>

            <p style="color: #666; line-height: 1.6;">
              I believe my skills and experience make me a strong candidate for this role. You can view my CV using the secure link below:
            </p>

            <div style="text-align: center; margin: 30px 0;">
              <a href="{{shareLink}}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold;">
                View CV
              </a>
            </div>

            <p style="color: #666; line-height: 1.6;">
              The link is secure and will expire on {{expiryDate}}. Please let me know if you have any questions.
            </p>

            <div style="border-top: 1px solid #eee; margin-top: 30px; padding-top: 20px; text-align: center; color: #999; font-size: 12px;">
              <p>This email was sent by {{senderName}} via CV Maker</p>
              <p>{{shareLink}}</p>
            </div>
          </div>
        </div>
      `,
      textTemplate: `
Hi {{firstName}},

I hope this email finds you well. I'm writing to share my updated CV with you regarding the {{position}} opportunity.

I believe my skills and experience make me a strong candidate for this role. You can view my CV using the secure link below:

{{shareLink}}

The link is secure and will expire on {{expiryDate}}. Please let me know if you have any questions.

Best regards,
{{senderName}}

---
This email was sent by {{senderName}} via CV Maker
{{shareLink}}
      `
    },
    {
      id: 'marriage_biodata',
      name: 'Marriage Biodata Share',
      subject: '{{firstName}}, please find my marriage biodata',
      category: 'marriage',
      isDefault: true,
      variables: ['firstName', 'senderName', 'relation', 'age'],
      htmlTemplate: `
        <div style="font-family: 'Georgia', serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px; text-align: center; border-radius: 15px;">
            <h1 style="margin: 0; font-size: 32px; font-family: 'Dancing Script', cursive;">Marriage Biodata</h1>
            <p style="margin: 15px 0 0 0; opacity: 0.9;">{{senderName}}, {{age}} years</p>
          </div>

          <div style="background: #fef7ff; padding: 30px; border-radius: 15px; border: 2px solid #f093fb;">
            <h2 style="color: #831843; margin-top: 0; text-align: center;">Dear {{firstName}},</h2>

            <p style="color: #1e293b; line-height: 1.7; text-align: center; font-size: 16px;">
              I hope this message finds you in good health and spirits. As part of our search for a suitable life partner,
              I am sharing my marriage biodata with you.
            </p>

            <p style="color: #1e293b; line-height: 1.7; text-align: center; font-size: 16px;">
              Please find attached my detailed biodata containing information about my education, profession, family background,
              and personal preferences.
            </p>

            <div style="text-align: center; margin: 35px 0;">
              <a href="{{shareLink}}" style="background: #f093fb; color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-weight: bold; font-size: 16px;">
                View Complete Biodata
              </a>
            </div>

            <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #f093fb;">
              <p style="color: #1e293b; margin: 0; font-size: 14px;">
                <strong>Important:</strong> This biodata is shared confidentially. The link will expire on {{expiryDate}}.
              </p>
            </div>

            <p style="color: #1e293b; line-height: 1.7; text-align: center; font-size: 16px;">
              Thank you for your time and consideration. I look forward to hearing from you.
            </p>

            <div style="text-align: center; margin-top: 30px; color: #64748b; font-size: 14px;">
              <p>Warm regards,<br>{{senderName}}</p>
            </div>

            <div style="border-top: 1px solid #f093fb; margin-top: 30px; padding-top: 20px; text-align: center; color: #64748b; font-size: 12px;">
              <p>This biodata was shared via CV Maker Marriage Portal</p>
              <p>{{shareLink}}</p>
            </div>
          </div>
        </div>
      `,
      textTemplate: `
Dear {{firstName}},

I hope this message finds you in good health and spirits. As part of our search for a suitable life partner,
I am sharing my marriage biodata with you.

Please find attached my detailed biodata containing information about my education, profession, family background,
and personal preferences.

View Complete Biodata: {{shareLink}}

Important: This biodata is shared confidentially. The link will expire on {{expiryDate}}.

Thank you for your time and consideration. I look forward to hearing from you.

Warm regards,
{{senderName}}

---
This biodata was shared via CV Maker Marriage Portal
{{shareLink}}
      `
    },
    {
      id: 'general_share',
      name: 'General Document Share',
      subject: '{{senderName}} has shared a document with you',
      category: 'general',
      isDefault: false,
      variables: ['firstName', 'senderName', 'documentName'],
      htmlTemplate: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="background: #f8f9fa; padding: 25px; border-radius: 8px; border-left: 4px solid #007bff;">
            <h2 style="color: #333; margin-top: 0;">Document Shared</h2>
            <p style="color: #666; margin: 0;">
              {{senderName}} has shared "{{documentName}}" with you
            </p>
          </div>

          <div style="padding: 20px;">
            <p style="color: #666; line-height: 1.6;">
              Hi {{firstName}},
            </p>

            <p style="color: #666; line-height: 1.6;">
              {{customMessage}}
            </p>

            <div style="text-align: center; margin: 25px 0;">
              <a href="{{shareLink}}" style="background: #007bff; color: white; padding: 10px 25px; text-decoration: none; border-radius: 5px;">
                View Document
              </a>
            </div>

            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 14px; color: #666;">
              <p style="margin: 0;"><strong>Note:</strong> This link will expire on {{expiryDate}}</p>
            </div>
          </div>
        </div>
      `,
      textTemplate: `
Hi {{firstName}},

{{senderName}} has shared "{{documentName}}" with you.

{{customMessage}}

View Document: {{shareLink}}

Note: This link will expire on {{expiryDate}}

Best regards,
{{senderName}}
      `
    }
  ];

  static async sendShareEmail(
    options: EmailShareOptions,
    documentInfo: {
      id: string;
      name: string;
      type: 'cv' | 'marriage' | 'general';
      shareLink: ShareableLink;
    }
  ): Promise<{
    success: boolean;
    emailId: string;
    errors?: string[];
    analytics?: EmailAnalytics;
  }> {
    try {
      // Validate recipients
      const validRecipients = this.validateEmails(options.recipients);
      if (validRecipients.length === 0) {
        return {
          success: false,
          emailId: '',
          errors: ['No valid email addresses provided']
        };
      }

      // Get template
      const template = this.getTemplate(options.templateId, documentInfo.type);
      if (!template) {
        return {
          success: false,
          emailId: '',
          errors: ['Template not found']
        };
      }

      // Create shareable link with privacy settings
      const privacyConfig = {
        ...options.privacy,
        watermarkText: `Shared with ${validRecipients[0]}`,
        expirationHours: 24 // Default 24 hours for email shares
      };

      // Prepare email content for each recipient
      const emailPromises = validRecipients.map(async (recipient) => {
        const variables = this.prepareVariables(recipient, documentInfo, options.customMessage);
        const { html, text } = this.renderTemplate(template, variables);

        // Add tracking pixel
        const trackedHtml = options.tracking?.enabled
          ? this.addTrackingPixel(html, options.tracking.uniqueId || this.generateTrackingId())
          : html;

        // Create email data
        const emailData = {
          to: recipient,
          subject: this.processTemplateString(template.subject, variables),
          html: trackedHtml,
          text: text,
          attachments: options.attachments
        };

        // Send email (placeholder implementation)
        return await this.sendEmail(emailData);
      });

      const results = await Promise.allSettled(emailPromises);

      // Create analytics
      const emailId = this.generateEmailId();
      const analytics: EmailAnalytics = {
        emailId,
        sentAt: new Date(),
        recipients: validRecipients,
        delivered: results.filter(r => r.status === 'fulfilled').length,
        opened: 0,
        clicked: 0,
        bounced: results.filter(r => r.status === 'rejected').length,
        unsubscribed: 0,
        trackingData: []
      };

      // Store analytics
      await this.storeEmailAnalytics(analytics);

      return {
        success: results.some(r => r.status === 'fulfilled'),
        emailId,
        errors: results
          .filter((r): r is PromiseRejectedResult => r.status === 'rejected')
          .map(r => r.reason.message || 'Unknown error'),
        analytics
      };
    } catch (error) {
      console.error('Error sending share email:', error);
      return {
        success: false,
        emailId: '',
        errors: [error instanceof Error ? error.message : 'Unknown error']
      };
    }
  }

  static async sendBulkEmail(
    options: BulkEmailOptions,
    documentInfo: {
      id: string;
      name: string;
      type: 'cv' | 'marriage' | 'general';
    }
  ): Promise<{
    success: boolean;
    campaignId: string;
    totalSent: number;
    totalFailed: number;
    analytics?: EmailAnalytics;
  }> {
    try {
      const template = this.TEMPLATES.find(t => t.id === options.templateId);
      if (!template) {
        throw new Error('Template not found');
      }

      const campaignId = this.generateCampaignId();
      const batchSize = options.scheduling?.batchSize || 50;
      const delay = options.scheduling?.delayBetweenBatches || 5000; // 5 seconds

      let totalSent = 0;
      let totalFailed = 0;
      const allAnalytics: EmailTracking[] = [];

      // Process recipients in batches
      for (let i = 0; i < options.recipients.length; i += batchSize) {
        const batch = options.recipients.slice(i, i + batchSize);
        const batchPromises = batch.map(async (recipient, index) => {
          try {
            const variables = {
              ...options.variables?.[i + index],
              firstName: this.extractFirstName(recipient),
              senderName: 'Current User', // Get from user context
              documentName: documentInfo.name,
              shareLink: await this.createShareLink(documentInfo.id, recipient),
              expiryDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toLocaleDateString()
            };

            const { html, text } = this.renderTemplate(template, variables);

            const emailData = {
              to: recipient,
              subject: this.processTemplateString(template.subject, variables),
              html: options.tracking?.enabled
                ? this.addTrackingPixel(html, `${campaignId}_${i + index}`)
                : html,
              text: text
            };

            await this.sendEmail(emailData);
            totalSent++;

            // Add tracking data
            allAnalytics.push({
              id: this.generateTrackingId(),
              timestamp: new Date(),
              action: 'sent',
              recipient,
              location: 'Unknown'
            });

            return true;
          } catch (error) {
            totalFailed++;
            console.error(`Failed to send email to ${recipient}:`, error);
            return false;
          }
        });

        await Promise.allSettled(batchPromises);

        // Delay between batches (except for the last batch)
        if (i + batchSize < options.recipients.length) {
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }

      // Store campaign analytics
      const analytics: EmailAnalytics = {
        emailId: campaignId,
        sentAt: new Date(),
        recipients: options.recipients,
        delivered: totalSent,
        opened: 0,
        clicked: 0,
        bounced: totalFailed,
        unsubscribed: 0,
        trackingData: allAnalytics
      };

      await this.storeEmailAnalytics(analytics);

      return {
        success: totalSent > 0,
        campaignId,
        totalSent,
        totalFailed,
        analytics
      };
    } catch (error) {
      console.error('Error sending bulk email:', error);
      return {
        success: false,
        campaignId: '',
        totalSent: 0,
        totalFailed: options.recipients.length
      };
    }
  }

  static createCustomTemplate(
    template: Omit<EmailTemplate, 'id'>
  ): EmailTemplate {
    return {
      ...template,
      id: this.generateTemplateId()
    };
  }

  static getAvailableTemplates(category?: 'cv' | 'marriage' | 'general'): EmailTemplate[] {
    if (category) {
      return this.TEMPLATES.filter(t => t.category === category);
    }
    return [...this.TEMPLATES];
  }

  static previewTemplate(
    templateId: string,
    variables: Record<string, string>
  ): { html: string; text: string } {
    const template = this.TEMPLATES.find(t => t.id === templateId);
    if (!template) {
      throw new Error('Template not found');
    }

    return this.renderTemplate(template, variables);
  }

  static async getEmailAnalytics(
    emailId: string
  ): Promise<EmailAnalytics | null> {
    try {
      const data = localStorage.getItem(`email_analytics_${emailId}`);
      if (!data) return null;

      const analytics = JSON.parse(data);
      return {
        ...analytics,
        sentAt: new Date(analytics.sentAt),
        trackingData: analytics.trackingData.map((tracking: any) => ({
          ...tracking,
          timestamp: new Date(tracking.timestamp)
        }))
      };
    } catch (error) {
      console.error('Error getting email analytics:', error);
      return null;
    }
  }

  static async trackEmailAction(
    trackingId: string,
    action: 'opened' | 'clicked' | 'bounced' | 'unsubscribed',
    recipient: string,
    additionalData?: {
      ipAddress?: string;
      userAgent?: string;
      location?: string;
    }
  ): Promise<void> {
    try {
      // Find the email analytics by tracking ID
      const allKeys = Object.keys(localStorage).filter(key => key.startsWith('email_analytics_'));

      for (const key of allKeys) {
        const data = localStorage.getItem(key);
        if (!data) continue;

        const analytics = JSON.parse(data);
        const trackingEntry = analytics.trackingData.find((t: any) =>
          t.recipient === recipient && t.id === trackingId
        );

        if (trackingEntry) {
          // Update the tracking entry
          trackingEntry.action = action;
          trackingEntry.timestamp = new Date().toISOString();

          if (additionalData) {
            Object.assign(trackingEntry, additionalData);
          }

          // Update counters
          switch (action) {
            case 'opened':
              analytics.opened++;
              break;
            case 'clicked':
              analytics.clicked++;
              break;
            case 'bounced':
              analytics.bounced++;
              break;
            case 'unsubscribed':
              analytics.unsubscribed++;
              break;
          }

          localStorage.setItem(key, JSON.stringify(analytics));
          break;
        }
      }
    } catch (error) {
      console.error('Error tracking email action:', error);
    }
  }

  private static validateEmails(emails: string[]): string[] {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emails.filter(email => emailRegex.test(email.trim()));
  }

  private static getTemplate(templateId?: string, documentType?: string): EmailTemplate | null {
    if (templateId) {
      return this.TEMPLATES.find(t => t.id === templateId) || null;
    }

    // Find default template for document type
    return this.TEMPLATES.find(t => t.category === documentType && t.isDefault) || null;
  }

  private static prepareVariables(
    recipient: string,
    documentInfo: any,
    customMessage?: string
  ): Record<string, string> {
    return {
      firstName: this.extractFirstName(recipient),
      senderName: 'Current User', // Get from user context
      documentName: documentInfo.name,
      shareLink: documentInfo.shareLink.url,
      expiryDate: new Date(documentInfo.shareLink.expiresAt).toLocaleDateString(),
      customMessage: customMessage || '',
      position: documentInfo.position || 'opportunity',
      company: documentInfo.company || 'your organization',
      relation: documentInfo.relation || 'friend',
      age: documentInfo.age || '25'
    };
  }

  private static renderTemplate(
    template: EmailTemplate,
    variables: Record<string, string>
  ): { html: string; text: string } {
    const html = this.processTemplateString(template.htmlTemplate, variables);
    const text = this.processTemplateString(template.textTemplate, variables);

    return { html, text };
  }

  private static processTemplateString(
    template: string,
    variables: Record<string, string>
  ): string {
    let result = template;

    for (const [key, value] of Object.entries(variables)) {
      const placeholder = `{{${key}}}`;
      result = result.replace(new RegExp(placeholder, 'g'), value);
    }

    return result;
  }

  private static addTrackingPixel(html: string, trackingId: string): string {
    const trackingPixel = `
      <img src="${window.location.origin}/api/email/track/${trackingId}"
           width="1" height="1" style="display: none;" alt="">
    `;

    return html.replace('</body>', `${trackingPixel}</body>`);
  }

  private static async sendEmail(emailData: {
    to: string;
    subject: string;
    html: string;
    text: string;
    attachments?: EmailAttachment[];
  }): Promise<void> {
    // This is a placeholder implementation
    // In a real application, you would integrate with an email service
    console.log('Sending email to:', emailData.to);
    console.log('Subject:', emailData.subject);
    console.log('Attachments:', emailData.attachments?.length || 0);

    // Simulate email sending
    await new Promise(resolve => setTimeout(resolve, 100));

    // In a real implementation, you would use:
    // - SendGrid
    // - Mailgun
    // - AWS SES
    // - Or any other email service
  }

  private static async createShareLink(documentId: string, recipient: string): Promise<string> {
    // Create a unique share link for this recipient
    const link = await ShareableLinkManager.createShareableLink({
      documentId,
      documentName: 'Document',
      accessLevel: 'restricted',
      expirationHours: 24,
      allowedEmails: [recipient],
      requireVerification: true
    });

    return link.url;
  }

  private static async storeEmailAnalytics(analytics: EmailAnalytics): Promise<void> {
    try {
      localStorage.setItem(`email_analytics_${analytics.emailId}`, JSON.stringify(analytics));
    } catch (error) {
      console.error('Error storing email analytics:', error);
    }
  }

  private static extractFirstName(email: string): string {
    const namePart = email.split('@')[0];
    return namePart.split('.')[0] || namePart.split('_')[0] || 'there';
  }

  private static generateEmailId(): string {
    return `email_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private static generateCampaignId(): string {
    return `campaign_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private static generateTemplateId(): string {
    return `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private static generateTrackingId(): string {
    return crypto.randomUUID();
  }
}