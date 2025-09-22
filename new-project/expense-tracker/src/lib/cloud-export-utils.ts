import { Expense } from '@/types/expense';
import {
  CloudExportJob,
  ExportTemplate,
  ExportSchedule,
  ShareableLink,
  ExportFormat,
  ExportDestination,
  ExportType
} from '@/types/cloud-export';
import QRCode from 'qrcode';

// Mock export templates
export const defaultTemplates: ExportTemplate[] = [
  {
    id: 'tax-report',
    name: 'Tax Report',
    description: 'Complete expense report for tax filing',
    format: 'pdf',
    destination: 'download',
    config: {},
    isDefault: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: 'monthly-summary',
    name: 'Monthly Summary',
    description: 'Monthly expense summary with category breakdown',
    format: 'pdf',
    destination: 'email',
    config: {
      emailConfig: {
        recipients: [],
        subject: 'Monthly Expense Summary',
        message: 'Here is your monthly expense summary.',
        includeSummary: true,
      },
    },
    isDefault: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: 'category-analysis',
    name: 'Category Analysis',
    description: 'Detailed analysis by spending categories',
    format: 'xlsx',
    destination: 'google-sheets',
    config: {},
    isDefault: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: 'real-time-sync',
    name: 'Real-time Google Sheets',
    description: 'Live sync expenses to Google Sheets',
    format: 'google-sheet',
    destination: 'google-sheets',
    config: {},
    isDefault: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
];

// Mock cloud integrations
export const mockIntegrations = [
  {
    id: 'google-sheets',
    name: 'Google Sheets',
    type: 'google-sheets' as const,
    isConnected: true,
    lastSync: new Date(Date.now() - 1000 * 60 * 5), // 5 minutes ago
    config: {
      googleSheets: {
        spreadsheetId: '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
        sheetName: 'Expenses',
        range: 'A:D',
      },
    },
  },
  {
    id: 'google-drive',
    name: 'Google Drive',
    type: 'google-drive' as const,
    isConnected: false,
    config: {
      googleDrive: {
        folderPath: '/Expense Reports',
      },
    },
  },
  {
    id: 'dropbox',
    name: 'Dropbox',
    type: 'dropbox' as const,
    isConnected: false,
    config: {
      googleDrive: {
        folderPath: '/Expense Reports',
      },
    },
  },
];

export class CloudExportService {
  private static instance: CloudExportService;
  private exportJobs: Map<string, CloudExportJob> = new Map();
  private schedules: ExportSchedule[] = [];
  private shareableLinks: ShareableLink[] = [];

  static getInstance(): CloudExportService {
    if (!CloudExportService.instance) {
      CloudExportService.instance = new CloudExportService();
    }
    return CloudExportService.instance;
  }

  async createExportJob(
    expenses: Expense[],
    type: ExportType,
    destination: ExportDestination,
    format: ExportFormat,
    template?: ExportTemplate
  ): Promise<CloudExportJob> {
    const jobId = this.generateId();
    const job: CloudExportJob = {
      id: jobId,
      status: 'pending',
      type,
      destination,
      format,
      template,
      progress: 0,
    };

    this.exportJobs.set(jobId, job);

    // Simulate processing
    this.processExportJob(jobId, expenses);

    return job;
  }

  private async processExportJob(jobId: string, expenses: Expense[]) {
    const job = this.exportJobs.get(jobId);
    if (!job) return;

    job.status = 'processing';
    job.progress = 10;

    // Simulate processing time
    await this.delay(1000);
    job.progress = 50;

    await this.delay(1000);
    job.progress = 90;

    // Generate export based on destination
    try {
      switch (job.destination) {
        case 'email':
          await this.simulateEmailExport(expenses, job);
          break;
        case 'google-sheets':
          await this.simulateGoogleSheetsExport(expenses, job);
          break;
        case 'download':
          await this.simulateDownloadExport(expenses, job);
          break;
        default:
          await this.simulateGenericExport(expenses, job);
      }

      job.status = 'completed';
      job.completedAt = new Date();
      job.progress = 100;
    } catch (error) {
      job.status = 'failed';
      job.error = error instanceof Error ? error.message : 'Unknown error';
    }
  }

  private async simulateEmailExport(expenses: Expense[], job: CloudExportJob) {
    // Simulate email sending
    await this.delay(500);
    job.downloadUrl = `https://expense-tracker.app/exports/${job.id}/download`;
    console.log(`Email export completed for job ${job.id}`);
  }

  private async simulateGoogleSheetsExport(expenses: Expense[], job: CloudExportJob) {
    // Simulate Google Sheets sync
    await this.delay(800);
    job.downloadUrl = `https://docs.google.com/spreadsheets/d/${this.generateId()}`;
    console.log(`Google Sheets export completed for job ${job.id}`);
  }

  private async simulateDownloadExport(expenses: Expense[], job: CloudExportJob) {
    // Simulate file generation
    await this.delay(300);
    job.downloadUrl = `https://expense-tracker.app/exports/${job.id}/download`;
    console.log(`Download export completed for job ${job.id}`);
  }

  private async simulateGenericExport(expenses: Expense[], job: CloudExportJob) {
    await this.delay(600);
    job.downloadUrl = `https://expense-tracker.app/exports/${job.id}/download`;
    console.log(`Generic export completed for job ${job.id}`);
  }

  async createShareableLink(jobId: string, isPublic: boolean = false, password?: string): Promise<ShareableLink> {
    const job = this.exportJobs.get(jobId);
    if (!job || job.status !== 'completed') {
      throw new Error('Export job must be completed before sharing');
    }

    const shareId = this.generateId();
    const shareableLink: ShareableLink = {
      id: shareId,
      exportId: jobId,
      url: `https://expense-tracker.app/share/${shareId}`,
      isPublic,
      password,
      viewCount: 0,
      downloadCount: 0,
      createdAt: new Date(),
    };

    this.shareableLinks.push(shareableLink);
    job.shareUrl = shareableLink.url;

    return shareableLink;
  }

  async generateQRCode(text: string): Promise<string> {
    return await QRCode.toDataURL(text, {
      width: 200,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#ffffff',
      },
    });
  }

  async createScheduledExport(templateId: string, frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly'): Promise<ExportSchedule> {
    const schedule: ExportSchedule = {
      id: this.generateId(),
      name: `${frequency} export - ${templateId}`,
      templateId,
      isActive: true,
      nextRun: this.calculateNextRun(frequency),
      frequency,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      exportCount: 0,
    };

    this.schedules.push(schedule);
    return schedule;
  }

  getExportJob(jobId: string): CloudExportJob | undefined {
    return this.exportJobs.get(jobId);
  }

  getAllExportJobs(): CloudExportJob[] {
    return Array.from(this.exportJobs.values()).sort(
      (a, b) => new Date(b.scheduledAt || 0).getTime() - new Date(a.scheduledAt || 0).getTime()
    );
  }

  getShareableLinks(): ShareableLink[] {
    return this.shareableLinks.sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  getSchedules(): ExportSchedule[] {
    return this.schedules;
  }

  private calculateNextRun(frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly'): Date {
    const now = new Date();
    const next = new Date(now);

    switch (frequency) {
      case 'daily':
        next.setDate(now.getDate() + 1);
        break;
      case 'weekly':
        next.setDate(now.getDate() + 7);
        break;
      case 'monthly':
        next.setMonth(now.getMonth() + 1);
        break;
      case 'quarterly':
        next.setMonth(now.getMonth() + 3);
        break;
    }

    return next;
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export const cloudExportService = CloudExportService.getInstance();