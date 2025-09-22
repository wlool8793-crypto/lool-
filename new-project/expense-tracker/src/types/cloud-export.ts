export interface CloudExportJob {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  type: ExportType;
  destination: ExportDestination;
  format: ExportFormat;
  template?: ExportTemplate;
  scheduledAt?: Date;
  completedAt?: Date;
  progress: number;
  error?: string;
  downloadUrl?: string;
  shareUrl?: string;
}

export type ExportType = 'manual' | 'scheduled' | 'shared' | 'integration';
export type ExportFormat = 'csv' | 'json' | 'pdf' | 'xlsx' | 'google-sheet';
export type ExportDestination =
  | 'download'
  | 'email'
  | 'google-drive'
  | 'dropbox'
  | 'onedrive'
  | 'google-sheets'
  | 'webhook';

export interface ExportTemplate {
  id: string;
  name: string;
  description: string;
  format: ExportFormat;
  destination: ExportDestination;
  config: TemplateConfig;
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface TemplateConfig {
  filters?: {
    dateRange?: { start: string; end: string };
    categories?: string[];
    amountRange?: { min: number; max: number };
  };
  emailConfig?: {
    recipients: string[];
    subject: string;
    message: string;
    includeSummary: boolean;
  };
  scheduleConfig?: {
    frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
    time: string; // HH:mm format
    timezone: string;
  };
  sharingConfig?: {
    isPublic: boolean;
    expiresAt?: Date;
    password?: string;
    allowDownload: boolean;
  };
}

export interface ExportSchedule {
  id: string;
  name: string;
  templateId: string;
  isActive: boolean;
  lastRun?: Date;
  nextRun: Date;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  timezone: string;
  exportCount: number;
}

export interface CloudIntegration {
  id: string;
  name: string;
  type: 'google-sheets' | 'google-drive' | 'dropbox' | 'onedrive' | 'webhook';
  isConnected: boolean;
  lastSync?: Date;
  config: IntegrationConfig;
}

export interface IntegrationConfig {
  googleSheets?: {
    spreadsheetId?: string;
    sheetName?: string;
    range?: string;
  };
  googleDrive?: {
    folderId?: string;
    folderPath?: string;
  };
  webhook?: {
    url: string;
    headers?: Record<string, string>;
    method: 'POST' | 'PUT';
  };
}

export interface ShareableLink {
  id: string;
  exportId: string;
  url: string;
  isPublic: boolean;
  password?: string;
  expiresAt?: Date;
  viewCount: number;
  downloadCount: number;
  createdAt: Date;
}

export interface ExportAnalytics {
  totalExports: number;
  formatDistribution: Record<ExportFormat, number>;
  destinationDistribution: Record<ExportDestination, number>;
  popularTemplates: Array<{ template: ExportTemplate; usage: number }>;
  sharingStats: {
    totalShares: number;
    publicShares: number;
    privateShares: number;
    totalViews: number;
    totalDownloads: number;
  };
}